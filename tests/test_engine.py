import copy,json,math,unittest
from unittest.mock import patch
from chat_engine import Catalog,Conversation,Provider,ProviderError,TOOLS
from chemistry_tools import arithmetic,check_step

class FakeProvider:
    configured=True
    def __init__(self,responses):self.responses=iter(responses);self.requests=[]
    def respond(self,history,instructions):
        self.requests.append((copy.deepcopy(history),instructions))
        return next(self.responses)
def message(text):return {'status':'completed','output':[{'type':'message','role':'assistant','content':[{'type':'output_text','text':text}]}]}
def call(name,args):return {'output':[{'type':'function_call','call_id':'test-call','name':name,'arguments':json.dumps(args)}]}

class ArithmeticTests(unittest.TestCase):
    def test_supported_arithmetic(self):
        for expression,answer in [('2+3*4',14),('sqrt(16)',4),('ln(exp(2))',2),('-log10(1e-3)',3),('2**-2',.25),('abs(-5)',5)]:
            with self.subTest(expression=expression):self.assertAlmostEqual(arithmetic(expression),answer)
    def test_rejects_code_and_resource_attacks(self):
        for expression in ['__import__("os").system("whoami")','[1,2][0]','(1).__class__','2**1000000','1/0','sqrt(-1)','exp(1000)','1e999','True','x+1','f()','2'*301,'(1,2)','sum([1])']:
            with self.subTest(expression=expression):
                with self.assertRaises((ValueError,SyntaxError)):arithmetic(expression)
    def test_hidden_calculation_and_small_numbers(self):
        self.assertEqual(check_step('6.626e-34*2.998e8/550e-9',0)['status'],'check_arithmetic')
        self.assertEqual(check_step('2*3',6)['status'],'arithmetic_matches')
        self.assertNotIn('answer',check_step('2*3',5));self.assertNotIn('6',check_step('2*3',5)['message'])
    def test_bad_claim(self):
        for claim in [math.nan,math.inf,'6',True,None]:
            with self.assertRaises(ValueError):check_step('2*3',claim)

class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.catalog=Catalog()
    def test_all_91_topics_selectable(self):
        for topic in self.catalog.topics:
            with self.subTest(topic=topic['id']):
                s,q=self.catalog.practice(topic['id'])
                self.assertEqual(q['topic_id'],topic['id']);self.assertNotIn('answer',q);self.assertNotIn('steps',q)
    def test_graph_question_receives_visible_stimulus(self):
        _,q=self.catalog.practice('3.4','graph-gas_pv-read',1)
        self.assertEqual(len(q['visual']['points']),201)
        self.assertNotIn('parameters',q['visual']);self.assertNotIn('equation',q['visual'])
    def test_graph_bounds(self):
        for v in [0,101,1.2,True,None]:
            with self.assertRaises(ValueError):self.catalog.graph('gas_pv',v)
        with self.assertRaises(ValueError):self.catalog.graph('../solutions',1)
    def test_unconfigured_is_honest(self):
        r=Conversation(self.catalog,Provider(key='',model='')).chat('explain equilibrium')
        self.assertEqual(r['status'],'model_not_configured');self.assertNotIn('model_response',json.dumps(r))
    def test_model_loop_retains_tool_calls_and_context(self):
        fake=FakeProvider([call('find_topics',{'query':'equilibrium'}),message('Which species belong in the expression?')])
        c=Conversation(self.catalog,fake);r=c.chat('Help me with equilibrium')
        self.assertEqual(r['status'],'model_response')
        self.assertTrue(any(i.get('type')=='function_call_output' for i in fake.requests[1][0]))
        self.assertEqual(len(c.messages),2)
    def test_current_answer_never_sent_to_model(self):
        fake=FakeProvider([message('Which law connects those variables?')]);c=Conversation(self.catalog,fake)
        c.start('3.4','ideal_gas',1);c.chat('Help me start')
        request=json.dumps(fake.requests)
        self.assertNotIn('Numerical result:',request);self.assertNotIn('"solution"',request)
        self.assertNotIn(str(c.practice._solution['answer']),request)
    def test_graph_tool_requires_request_and_no_active_practice(self):
        c=Conversation(self.catalog);args={'family_id':'gas_pv','variant':1}
        self.assertIsNone(c.tool('show_graph',args,'tell me about gases')[1])
        self.assertEqual(c.tool('show_graph',args,'show me a graph')[1]['dataset_id'],'gas_pv-01')
        c.start('3.4','ideal_gas',1);self.assertIsNone(c.tool('show_graph',args,'show me a graph')[1])
    def test_model_cannot_invent_attempt(self):
        c=Conversation(self.catalog)
        self.assertEqual(c.tool('check_arithmetic_step',{'expression':'2*3','claimed':6},'give me the answer')[0]['status'],'attempt_needed')
    def test_unknown_tool_cannot_execute(self):
        fake=FakeProvider([call('run_shell',{'cmd':'echo hidden'}),message('Let us review the setup.')])
        c=Conversation(self.catalog,fake);r=c.chat('help')
        self.assertEqual(r['checks'][0]['result']['status'],'invalid_request')
    def test_tool_loop_is_bounded(self):
        fake=FakeProvider([call('find_topics',{'query':'gas'})]*5)
        with self.assertRaises(ProviderError):Conversation(self.catalog,fake).chat('help')
        self.assertEqual(len(fake.requests),5)
    def test_failed_model_turn_does_not_pollute_history(self):
        fake=FakeProvider([{'status':'incomplete','output':[]}]);c=Conversation(self.catalog,fake)
        with self.assertRaises(ProviderError):c.chat('help')
        self.assertEqual(c.messages,[])
    def test_strict_tool_schemas(self):
        for t in TOOLS:
            self.assertTrue(t['strict']);self.assertFalse(t['parameters']['additionalProperties'])
            self.assertEqual(set(t['parameters']['required']),set(t['parameters']['properties']))
    def test_payload_bounds(self):
        c=Conversation(self.catalog)
        for text in ['',None,123,'x'*6001]:
            with self.assertRaises(ValueError):c.chat(text)
    def test_provider_http_contract(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return json.dumps(message('Which quantity is conserved?')).encode()
        with patch('chat_engine.urlopen',return_value=Response()) as request:
            # Select the provider explicitly so a developer's real
            # AI_PROVIDER environment cannot change this contract test.
            p=Provider(key='fake-key-for-contract-test',model='test-model',provider='openai')
            p.respond([{'role':'user','content':'test'}],'system')
            body=json.loads(request.call_args.args[0].data)
            self.assertFalse(body['store']);self.assertEqual(body['model'],'test-model')
            self.assertEqual(request.call_args.args[0].full_url,'https://api.openai.com/v1/responses')

    def test_groq_provider_contract(self):
        p=Provider(key='fake-groq-key',model='openai/gpt-oss-120b',provider='groq')
        self.assertTrue(p.configured)
        self.assertEqual(p.url,'https://api.groq.com/openai/v1/responses')
        self.assertEqual(p.model,'openai/gpt-oss-120b')

    def test_groq_selected_from_environment(self):
        with patch.dict('os.environ',{'AI_PROVIDER':'groq','GROQ_API_KEY':'test','GROQ_MODEL':'openai/gpt-oss-120b'},clear=True):
            p=Provider()
        self.assertTrue(p.configured)
        self.assertEqual(p.url,'https://api.groq.com/openai/v1/responses')

    def test_invalid_provider_rejected(self):
        with self.assertRaises(ValueError):Provider(provider='unknown')


class ConservationTests(unittest.TestCase):
    def test_formula_parentheses_and_ions(self):
        from chemistry_tools import formula_counts
        self.assertEqual(formula_counts('Ca(NO3)2'),({'Ca':1,'N':2,'O':6},0))
        self.assertEqual(formula_counts('SO4^2-(aq)'),({'S':1,'O':4},-2))
        self.assertEqual(formula_counts('e^-'),({},-1))
    def test_conservation_including_charge(self):
        from chemistry_tools import check_balance
        for equation in ['2 H2 + O2 -> 2 H2O','Ag^+ + Cl^- -> AgCl(s)','Fe^3+ + e^- -> Fe^2+','N2 + 3 H2 <-> 2 NH3']:
            with self.subTest(equation=equation):self.assertEqual(check_balance(equation)['status'],'conserved')
        self.assertEqual(check_balance('H2 + O2 -> H2O')['status'],'not_conserved')
        self.assertEqual(check_balance('Fe^3+ -> Fe^2+')['status'],'not_conserved')
    def test_invalid_formula_grammar(self):
        from chemistry_tools import formula_counts,check_balance
        for f in ['Xx2','H0','H2(','()','Ca(OH))','CuSO4.5H2O','Fe^99+','2H2','']:
            with self.subTest(formula=f):
                with self.assertRaises(ValueError):formula_counts(f)
        with self.assertRaises(ValueError):check_balance('0 H2 + O2 -> H2O')
    def test_100_balanced_and_100_mutated_reactions(self):
        from chemistry_tools import check_balance
        for i in range(1,101):
            self.assertEqual(check_balance(f'{2*i} H2 + {i} O2 -> {2*i} H2O')['status'],'conserved')
            self.assertEqual(check_balance(f'{2*i+1} H2 + {i} O2 -> {2*i} H2O')['status'],'not_conserved')

class UnitConversionTests(unittest.TestCase):
    def test_common_equivalents(self):
        from units import convert
        for value,source,target,expected in [(250,'mmol','mol',.25),(1,'kJ','J',1000),(101.325,'kPa','atm',1),(1,'M','mol/L',1),(2,'min','s',120),(.5,'L','mL',500)]:
            with self.subTest(source=source,target=target):self.assertAlmostEqual(convert(value,source,target),expected)
    def test_wrong_dimension_and_capitalization(self):
        from units import convert
        for source,target in [('g','mol'),('m','M'),('mol','dimensionless'),('pa','atm')]:
            with self.assertRaises(ValueError):convert(1,source,target)
    def test_grader_accepts_converted_units(self):
        c=Catalog();session,_=c.practice('1.1','moles',1)
        self.assertEqual(session.submit(str(session._solution['answer']*1000),'mmol')['status'],'correct')

if __name__=='__main__':unittest.main()

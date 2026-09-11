import unittest
from chat_engine import Catalog, Conversation, Provider
from test_engine import FakeProvider, message, call

class RetrievalRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.catalog=Catalog()

    def test_offline_guidance_has_no_solution_and_keeps_history(self):
        c=Conversation(self.catalog,Provider(key='',model=''))
        q='Why do equal masses of helium and neon contain different numbers of atoms?'
        r=c.chat(q)
        self.assertEqual(r['provider_calls'],0)
        self.assertEqual(r['status'],'local_retrieval')
        self.assertNotIn('helium has',r['message'])
        self.assertEqual(len(c.messages),2)

    def test_negated_query_does_not_reuse_answer(self):
        p=FakeProvider([message('Let us check that assumption.')])
        c=Conversation(self.catalog,p)
        r=c.chat('Why do equal masses of helium and neon NOT contain different numbers of atoms?')
        self.assertEqual(r['status'],'model_response')

    def test_counts_every_tool_round(self):
        a=call('find_topics',{'query':'equilibrium'})
        a['usage']={'input_tokens':100,'output_tokens':10,'total_tokens':110}
        b=message('What species are present?')
        b['usage']={'input_tokens':150,'output_tokens':20,'total_tokens':170}
        r=Conversation(self.catalog,FakeProvider([a,b])).chat('Help with equilibrium')
        self.assertEqual(r['provider_calls'],2)
        self.assertEqual(r['usage']['total_tokens'],280)

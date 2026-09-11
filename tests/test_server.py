import http.client,json,threading,unittest
from chat_engine import Provider
from server import App,make_server

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=App(provider=Provider(key='',model=''));cls.server=make_server(0,cls.app)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,method,path,data=None,headers=None):
        con=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        h={'Content-Type':'application/json'};h.update(headers or {})
        con.request(method,path,json.dumps(data) if data is not None else None,h)
        r=con.getresponse();body=r.read();result=(r.status,dict(r.getheaders()),body);con.close();return result
    def token(self):return json.loads(self.request('POST','/api/session',{})[2])['token']
    def test_private_files_not_served(self):
        for path in ['/corpus/chemistry.sqlite','/corpus/solutions.jsonl','/chat_engine.py','/.env','/../tutor.py','/api/solutions']:
            with self.subTest(path=path):self.assertEqual(self.request('GET',path)[0],404)
    def test_local_origin_and_host(self):
        self.assertEqual(self.request('POST','/api/session',{}, {'Origin':'https://evil.example'})[0],403)
        self.assertEqual(self.request('GET','/api/catalog',headers={'Host':'evil.example'})[0],403)
    def test_auth_required(self):
        self.assertEqual(self.request('POST','/api/practice',{'topic':'3.4'})[0],401)
    def test_session_isolation_and_hint_flow(self):
        a,b=self.token(),self.token();ha={'Authorization':'Bearer '+a};hb={'Authorization':'Bearer '+b}
        status,_,body=self.request('POST','/api/practice',{'topic':'3.4','family':'ideal_gas','variant':1},ha)
        self.assertEqual(status,200);self.assertNotIn('"answer":',body.decode());self.assertNotIn('steps',body.decode())
        self.assertEqual(self.request('POST','/api/hint',{},hb)[0],400)
        self.assertEqual(json.loads(self.request('POST','/api/hint',{},ha)[2])['status'],'hint')
        self.assertEqual(json.loads(self.request('POST','/api/hint',{},ha)[2])['status'],'attempt_needed')
        self.assertEqual(self.request('POST','/api/graph',{'family':'gas_pv','variant':1},ha)[0],400)
        self.assertEqual(self.request('POST','/api/graph',{'family':'gas_pv','variant':1},hb)[0],200)
    def test_malformed_payload_and_unknown_route(self):
        h={'Authorization':'Bearer '+self.token()}
        self.assertEqual(self.request('POST','/api/step',{'expression':'1/0','claimed':0},h)[0],200)
        self.assertEqual(self.request('POST','/api/step',{'expression':'1','claimed':float('nan')},h)[0],400)
        self.assertEqual(self.request('POST','/api/chat',{'text':'a'*17000},h)[0],413)
        self.assertEqual(self.request('POST','/api/unknown',{},h)[0],404)
    def test_no_model_response_fabricated(self):
        h={'Authorization':'Bearer '+self.token()}
        r=json.loads(self.request('POST','/api/chat',{'text':'Why is water polar?'},h)[2])
        self.assertEqual(r['status'],'model_not_configured')
    def test_security_headers(self):
        _,headers,_=self.request('GET','/api/catalog')
        self.assertEqual(headers['Cache-Control'],'no-store');self.assertIn("frame-ancestors 'none'",headers['Content-Security-Policy'])
    def test_rate_limit(self):
        h={'Authorization':'Bearer '+self.token()}
        for _ in range(30):self.assertEqual(self.request('POST','/api/step',{'expression':'1','claimed':1},h)[0],200)
        self.assertEqual(self.request('POST','/api/step',{'expression':'1','claimed':1},h)[0],400)

if __name__=='__main__':unittest.main()

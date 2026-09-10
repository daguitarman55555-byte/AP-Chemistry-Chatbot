"""Local single-user web server. Bind only to loopback; put authenticated infrastructure in front of any future deployment."""
import argparse,json,mimetypes,secrets,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from chat_engine import Catalog,Conversation,Provider,ProviderError
from chemistry_tools import check_step,check_balance

ROOT=Path(__file__).resolve().parent
class App:
    def __init__(self,catalog=None,provider=None):
        self.catalog=catalog or Catalog();self.provider=provider or Provider();self.sessions={};self.lock=threading.Lock()
    def new(self):
        with self.lock:
            now=time.monotonic()
            self.sessions={k:v for k,v in self.sessions.items() if now-v['used']<3600}
            if len(self.sessions)>=100: raise ValueError('Too many sessions; restart the local server to clear them')
            token=secrets.token_urlsafe(32)
            self.sessions[token]={'conversation':Conversation(self.catalog,self.provider),'used':now,'lock':threading.Lock(),'requests':[]}
            return token
    def session(self,token):
        with self.lock:
            entry=self.sessions.get(token);now=time.monotonic()
            if not entry or now-entry['used']>3600: raise PermissionError('Session expired. Reload the page.')
            entry['requests']=[t for t in entry['requests'] if now-t<60]
            if len(entry['requests'])>=30: raise ValueError('Request limit reached. Wait a minute before retrying.')
            entry['requests'].append(now);entry['used']=now
            return entry

def handler_for(app):
    class Handler(BaseHTTPRequestHandler):
        server_version='ChemistryStudio'
        def setup(self):
            super().setup();self.connection.settimeout(45)
        def log_message(self,*args): pass  # No student messages, tokens, or provider errors in logs.
        def allowed(self):
            host=self.headers.get('Host','')
            valid={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
            origin=self.headers.get('Origin')
            return host in valid and (origin is None or origin in {f'http://{h}' for h in valid})
        def send(self,status,data,kind='application/json; charset=utf-8'):
            raw=json.dumps(data,allow_nan=False).encode() if kind.startswith('application/json') else data
            self.send_response(status)
            self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            if not self.allowed(): return self.send(403,{'error':'Local origin required'})
            path=urlsplit(self.path).path
            if path=='/api/catalog': return self.send(200,app.catalog.public()|{'model_configured':app.provider.configured})
            if path=='/api/evidence':
                file=ROOT/'evidence/coverage.json'
                return self.send(200,json.loads(file.read_text()) if file.exists() else {'status':'Run python audit.py first'})
            # Never serve the project root: answer keys, credentials and database are private.
            public=(ROOT/'web/dist').resolve()
            target=(public/('index.html' if path=='/' else path.lstrip('/'))).resolve()
            if public not in target.parents or not target.is_file(): return self.send(404,{'error':'Not found'})
            return self.send(200,target.read_bytes(),mimetypes.guess_type(target.name)[0] or 'application/octet-stream')
        def do_POST(self):
            if not self.allowed(): return self.send(403,{'error':'Local origin required'})
            if self.headers.get('Content-Type','').split(';')[0]!='application/json': return self.send(415,{'error':'JSON required'})
            try:
                n=int(self.headers.get('Content-Length','0'))
                if not 0<n<=16384: return self.send(413,{'error':'Request must be 1–16384 bytes'})
                payload=json.loads(self.rfile.read(n),parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
                if not isinstance(payload,dict): raise ValueError('JSON object required')
                path=urlsplit(self.path).path
                if path=='/api/session': return self.send(200,{'token':app.new()})
                auth=self.headers.get('Authorization','')
                if not auth.startswith('Bearer '): raise PermissionError('Session token required')
                entry=app.session(auth[7:]);c=entry['conversation']
                if not entry['lock'].acquire(blocking=False): return self.send(409,{'error':'A request is already running for this session'})
                try:
                    if path=='/api/practice': result=c.start(payload.get('topic'),payload.get('family'),payload.get('variant'))
                    elif path=='/api/end': result=c.end()
                    elif path=='/api/hint':
                        if not c.practice: raise ValueError('Start a practice question first')
                        result=c.practice.hint()
                    elif path=='/api/attempt':
                        if not c.practice: raise ValueError('Start a practice question first')
                        result=c.practice.submit(payload.get('text',''),payload.get('unit'))
                    elif path=='/api/step': result=check_step(payload.get('expression'),payload.get('claimed'))
                    elif path=='/api/balance': result=check_balance(payload.get('equation'))
                    elif path=='/api/chat': result=c.chat(payload.get('text'))
                    elif path=='/api/graph':
                        if c.practice: raise ValueError('End practice before exploring another graph')
                        result={'visual':app.catalog.graph(payload.get('family'),payload.get('variant'))}
                    else: return self.send(404,{'error':'Unknown route'})
                    return self.send(200,result)
                finally: entry['lock'].release()
            except PermissionError as exc: self.send(401,{'error':str(exc)})
            except (ValueError,TypeError,KeyError) as exc: self.send(400,{'error':str(exc)})
            except ProviderError as exc: self.send(502,{'error':str(exc)})
            except Exception: self.send(500,{'error':'The server could not complete this request.'})
    return Handler

def make_server(port=8000,app=None): return ThreadingHTTPServer(('127.0.0.1',port),handler_for(app or App()))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8000);args=parser.parse_args()
    server=make_server(args.port)
    print(f'Chemistry Studio: http://127.0.0.1:{server.server_port}',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

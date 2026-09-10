"""Build missing assets and open the local tutor. No credentials are stored by this launcher."""
import argparse,os,shutil,subprocess,sys,threading,webbrowser
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rebuild',action='store_true');parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--no-browser',action='store_true');args=parser.parse_args()
    os.chdir(ROOT)
    if sys.version_info<(3,10):raise SystemExit('Python 3.10 or newer is required.')
    if args.rebuild or not (ROOT/'corpus/chemistry.sqlite').exists():
        print('Building the original chemistry practice bank…',flush=True)
        subprocess.run([sys.executable,'corpus/rebuild_all.py'],check=True)
    if args.rebuild or not (ROOT/'web/dist/index.html').exists():
        npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
        if not npm:raise SystemExit('Node.js with npm is required for the first build. Install Node.js 22 or newer, then start again.')
        subprocess.run([npm,'ci','--prefix','web','--ignore-scripts'],check=True)
        subprocess.run([npm,'run','build','--prefix','web'],check=True)
    subprocess.run([sys.executable,'audit.py'],check=True)
    from server import make_server
    server=make_server(args.port)
    url=f'http://127.0.0.1:{server.server_port}'
    print('\nOpen '+url+'\nKeep this window open. Press Ctrl+C to stop.',flush=True)
    if not (os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_MODEL')):
        print('Practice tools are ready. Open-ended AI chat is not configured.',flush=True)
    if not args.no_browser:threading.Timer(.5,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()

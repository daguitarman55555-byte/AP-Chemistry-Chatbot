"""Local journal of student questions for later review; never used as trusted facts."""
import hashlib,sqlite3,time
from pathlib import Path

def open_log(path=None):
    p=Path(path or Path(__file__).resolve().parent/'corpus/user_questions.sqlite')
    con=sqlite3.connect(p)
    con.execute('CREATE TABLE IF NOT EXISTS user_questions (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at REAL NOT NULL, session_hash TEXT NOT NULL, question TEXT NOT NULL, route TEXT NOT NULL, provider TEXT NOT NULL, reviewed INTEGER NOT NULL DEFAULT 0)')
    con.commit();return con

def record(question,session_id='',route='chat',provider='unknown',path=None):
    if not isinstance(question,str) or not question.strip(): return None
    text=question.strip()[:6000]
    digest=hashlib.sha256(str(session_id).encode()).hexdigest()[:16]
    with open_log(path) as con:
        cur=con.execute('INSERT INTO user_questions(created_at,session_hash,question,route,provider) VALUES(?,?,?,?,?)',(time.time(),digest,text,route,provider))
        con.commit();return cur.lastrowid

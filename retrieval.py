"""Small, deterministic local retriever for authored AP Chemistry knowledge chunks."""
import math,re
from collections import Counter

STOP=set('a an and are as at be by can do does for from how i in is it me of on or the this to what when where which why with you your'.split())
TOKEN=re.compile(r'[a-z0-9]+')

def terms(text): return [t for t in TOKEN.findall(text.lower()) if t not in STOP and len(t)>1]

class Retriever:
    def __init__(self,chunks):
        self.chunks=chunks;self.documents=[Counter(terms(c['title']+' '+c['question']+' '+c['text'])) for c in chunks]
        n=max(len(chunks),1);df=Counter()
        for doc in self.documents:df.update(doc.keys())
        self.idf={word:math.log((n+1)/(count+1))+1 for word,count in df.items()}
    def search(self,query,limit=3,exclude_topic=None):
        q=Counter(terms(query));scored=[]
        if not q:return []
        for chunk,doc in zip(self.chunks,self.documents):
            if chunk['topic_id']==exclude_topic:continue
            overlap=set(q)&set(doc)
            score=sum(self.idf.get(w,1)*min(q[w],doc[w]) for w in overlap)/math.sqrt(sum(q.values())*max(sum(doc.values()),1))
            if score:scored.append((score,chunk))
        return [dict(chunk,score=round(score,4)) for score,chunk in sorted(scored,key=lambda x:(-x[0],x[1]['topic_id']))[:limit]]

def compact_context(matches,max_chars=1800):
    pieces=[];used=0
    for m in matches:
        piece=f"[{m['topic_id']} {m['title']}] {m['text']} Source: {m['source_url']}"
        if used+len(piece)>max_chars:break
        pieces.append(piece);used+=len(piece)
    return '\n'.join(pieces)

"""Opt-in live smoke evaluation. Requires credentials and incurs API usage. Not a chemistry-certification test."""
import argparse,json,os,sys
from pathlib import Path
from chat_engine import Catalog,Conversation,Provider,ProviderError
ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--limit',type=int,default=9);p.add_argument('--output',default='live-evaluation.local.json');args=p.parse_args()
    if not 1<=args.limit<=91:p.error('Limit must be 1–91')
    provider=Provider()
    if not provider.configured:raise SystemExit('NOT RUN: configure OPENAI_API_KEY and OPENAI_MODEL in the server environment. Never paste keys into chat or commit them.')
    catalog=Catalog();rows=[]
    # Interleave units to exercise the whole course in the first nine prompts.
    topics=sorted(catalog.topics,key=lambda t:(int(t['id'].split('.')[1]),t['unit_id']))[:args.limit]
    for t in topics:
        with catalog.connect() as con:
            q=json.loads(con.execute('SELECT data_json FROM questions WHERE id=?',('C-'+t['id'],)).fetchone()[0])
        prompt=q['prompt']+' Please guide me without giving the answer.'
        try:
            response=Conversation(catalog,provider).chat(prompt)
            rows.append(dict(topic=t['id'],prompt=prompt,response=response,status='returned',expert_chemistry_review='pending',answer_leakage_review='pending'))
        except ProviderError as exc:rows.append(dict(topic=t['id'],status='failed',error=str(exc)))
    Path(args.output).write_text(json.dumps(dict(model=provider.model,scope='live response availability, not correctness proof',cases=rows),indent=2))
    print(f'{sum(r["status"]=="returned" for r in rows)}/{len(rows)} responses returned. All chemistry and pedagogy evaluations still require review.')
if __name__=='__main__':main()

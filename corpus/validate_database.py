"""Meaningful cross-checks: values, conservation, graph references, and answer separation."""
from pathlib import Path
import json,sqlite3,math
P=Path(__file__).resolve().parent
d=json.loads((P/'chemistry_database.json').read_text());qs={q['id']:q for q in d['questions']};ss={s['question_id']:s for s in d['solutions']}
gs={g['id']:g for g in map(json.loads,(P/'graph_datasets.jsonl').read_text().splitlines())}
assert len(qs)==len(d['questions'])==len(ss)
assert len({q['prompt'] for q in qs.values()})==len(qs)
assert len(d['topics'])==91
assert {s for q in qs.values() for s in q['science_practices']}==set(range(1,7))
assert all('answer' not in q and 'steps' not in q for q in qs.values())
count=0
for qid,q in qs.items():
    sol=ss[qid]
    assert sol['steps'] and any(h['question_id']==qid for h in d['hints'])
    if q.get('graph_dataset_id'):
        graph=gs[q['graph_dataset_id']]; p0,p1,p2=[graph['points'][j] for j in [40,90,150]]
        if q['family_id'].endswith('difference_of_changes'): expected=p2['y']-2*p1['y']+p0['y']
        elif q['family_id'].endswith('secant'): expected=(p2['y']-p0['y'])/(p2['x']-p0['x'])
        elif q['family_id'].endswith('change'): expected=p2['y']-p0['y']
        else: expected=p1['y']
        assert math.isclose(sol['answer'],expected,rel_tol=1e-10,abs_tol=1e-12),(qid,sol['answer'],expected)
        count+=1
    elif q['family_id']=='weak_acid':
        # Independent bisection for the model used by base weak-acid questions.
        C=q['parameters']['C']; K=q['parameters']['Ka']; lo=0;hi=C
        for _ in range(100):
            x=(lo+hi)/2
            if x*x>K*(C-x):hi=x
            else:lo=x
        assert abs(sol['answer']+math.log10((lo+hi)/2))<1e-10
    elif q['family_id']=='limiting':
        p=q['parameters'];a=sol['answer'];assert p['na']-2*a>=-1e-14 and p['nb']-a>=-1e-14

for g in gs.values():
    pts=g['points'];assert len(pts)==201 and all(math.isfinite(p['x']) and math.isfinite(p['y']) for p in pts)
    f=g['family_id'];ys=[p['y'] for p in pts]
    if f in ['transmittance','acid_speciation']:assert all(0<=y<=1 for y in ys)
    if f in ['first_order','second_order','common_ion']:assert all(a>=b for a,b in zip(ys,ys[1:]))
    if f=='strong_acid_titration':assert abs(ys[100]-7)<1e-6
    if f=='weak_acid_titration':assert ys[0]<7<ys[-1] and all(a<=b for a,b in zip(ys,ys[1:]))
con=sqlite3.connect(P/'chemistry.sqlite')
assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not con.execute('PRAGMA foreign_key_check').fetchall()
assert con.execute('SELECT COUNT(*) FROM questions').fetchone()[0]==len(qs)
assert con.execute('SELECT COUNT(*) FROM graph_datasets').fetchone()[0]==len(gs)
cols=[x[1] for x in con.execute('PRAGMA table_info(student_questions)')];assert cols==['id','topic_id','family_id','prompt']
coverage=json.loads((P/'coverage_200_types_per_topic.json').read_text())
for c in coverage:
    assert c['authored_family_count']==len({q['family_id'] for q in qs.values() if q['topic_id']==c['topic_id']})
    assert not c['requirement_met'] and c['expert_validated_distinct_types']==0
print(json.dumps(dict(question_records=len(qs),graph_answer_checks=count,graph_datasets=len(gs),
    weak_acid_roots='independently bisected',limiting_amounts='nonnegative',database_integrity='ok',
    expert_validation='not performed',coverage_target='unmet'),indent=2))

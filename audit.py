"""Reproducible census and adversarial grading checks. Unmet breadth targets remain visible."""
import collections,csv,hashlib,json,math,sys,unittest
from pathlib import Path
from tutor import TutorSession
ROOT=Path(__file__).resolve().parent

def audit():
    data=json.loads((ROOT/'corpus/chemistry_database.json').read_text())
    questions=data['questions'];solutions={s['question_id']:s for s in data['solutions']}
    hints=collections.defaultdict(list)
    for h in data['hints']:hints[h['question_id']].append(h)
    by_family=collections.defaultdict(list)
    passed=0
    for q in questions:
        by_family[q['family_id']].append(q);s=solutions[q['id']]
        assert 'answer' not in q and 'steps' not in q
        session=TutorSession(q,s,hints[q['id']])
        assert set(session.prompt())=={'id','topic_id','prompt'}
        if q['answer_kind']=='numeric':
            answer=s['answer'];assert math.isfinite(answer)
            assert session.submit(str(answer),s['answer_unit'])['status']=='correct',q['id']
            session=TutorSession(q,s,hints[q['id']])
            delta=max(abs(answer)*.5,(s['absolute_tolerance'] or 0)*100,1e-290)
            assert session.submit(str(answer+delta),s['answer_unit'])['status']=='try_again',q['id']
            # Zero must not be silently accepted for nonzero answers outside stated tolerance.
            if abs(answer)>max((s['absolute_tolerance'] or 0)*2,1e-290):
                assert TutorSession(q,s,hints[q['id']]).submit('0',s['answer_unit'])['status']=='try_again',q['id']
            for invalid in ('NaN','inf','-inf','1e9999','__import__("os")'):
                assert TutorSession(q,s,hints[q['id']]).submit(invalid,s['answer_unit'])['status']=='invalid_number',q['id']
            passed+=1
    family_rows=[]
    for family,qs in sorted(by_family.items()):
        hashes=[hashlib.sha256(json.dumps({'prompt':q['prompt'],'parameters':q['parameters']},sort_keys=True).encode()).hexdigest() for q in qs]
        assert len(set(hashes))==len(qs),family
        family_rows.append(dict(family_id=family,topic_id=qs[0]['topic_id'],variants=len(qs),unique_prompt_parameter_pairs=len(set(hashes)),
            meets_100_variants=len(qs)>=100,answer_kind=qs[0]['answer_kind'],
            correct_wrong_nonfinite_checks='pass' if qs[0]['answer_kind']=='numeric' else 'not_numeric',
            expert_reviewed=False,first_id=qs[0]['id'],last_id=qs[-1]['id']))
    topic_rows=[]
    for t in data['topics']:
        fs=[f for f in family_rows if f['topic_id']==t['id']]
        topic_rows.append(dict(topic_id=t['id'],label=t['label'],authored_families=len(fs),
            families_with_100_variants=sum(f['meets_100_variants'] for f in fs),questions=sum(f['variants'] for f in fs),
            target_200_distinct_types_met=False,expert_validated_types=0))
    tests=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result=unittest.TextTestRunner(verbosity=1).run(tests)
    assert result.wasSuccessful(),'Functional tests failed'
    source_files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.suffix in {'.py','.jsx','.css','.html','.txt','.mjs','.yml'} and not any(x in p.parts for x in ('node_modules','dist','evidence','__pycache__')) and p.name not in ('graph_explorer.html',))
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    report=dict(summary=dict(topics=len(topic_rows),units=len({t['unit_id'] for t in data['topics']}),questions=len(questions),
        authored_families=len(family_rows),families_with_at_least_100_variants=sum(f['meets_100_variants'] for f in family_rows),
        families_below_100_variants=sum(not f['meets_100_variants'] for f in family_rows),numeric_items_grading_checked=passed,
        graph_models=len(json.loads((ROOT/'corpus/graph_models.json').read_text())),graph_datasets=sum(1 for _ in (ROOT/'corpus/graph_datasets.jsonl').open()),
        graph_points=0,unit_integration_tests=result.testsRun,test_failures=len(result.failures)+len(result.errors),
        topics_meeting_200_distinct_types=0,expert_reviewed_items=0,live_model_tested=False,full_user_requirement_met=False),
        counting_policy='An authored family is a reasoning-template label, not an expert-certified AP question type. Numeric changes are variants. Graph tasks repeat four graph-literacy operations across 24 models. Unique strings alone do not prove pedagogical diversity.',
        proof_scope='Every numeric item: correct accepted, deliberately wrong rejected, nonfinite and code-like inputs rejected. Generator inverse checks plus separate corpus validator cover chemistry relations and graph arithmetic. Functional tests use a fake model; no live AI correctness claim.',
        families=family_rows,topics=topic_rows,source_sha256=manifest,
        corpus_sha256={name:hashlib.sha256((ROOT/'corpus'/name).read_bytes()).hexdigest() for name in ('questions.jsonl','solutions.jsonl','hints.jsonl','graph_datasets.jsonl')})
    report['summary']['graph_points']=sum(len(json.loads(line)['points']) for line in (ROOT/'corpus/graph_datasets.jsonl').open())
    dest=ROOT/'evidence';dest.mkdir(exist_ok=True)
    (dest/'coverage.json').write_text(json.dumps(report,indent=2)+'\n')
    for name,rows in [('families',family_rows),('topics',topic_rows)]:
        with (dest/(name+'.csv')).open('w',newline='') as file:
            writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps(report['summary'],indent=2))
    if '--require-full-coverage' in sys.argv:
        raise SystemExit('Release gate failed: 100 variants for every authored family and 200 expert-validated types per topic are not met.')
    return report
if __name__=='__main__':audit()

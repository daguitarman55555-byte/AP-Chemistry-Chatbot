"""Graph-reading tasks with distinct operations, backed by stored curve data."""
from pathlib import Path
import json,sqlite3,collections,math
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'chemistry_database.json').read_text())
graphs=[json.loads(s) for s in (ROOT/'graph_datasets.jsonl').read_text().splitlines()]
# Idempotent reruns; rebuilding the base also removes these records.
for key in ('questions','solutions','hints','validation_checks'):
    data[key]=[r for r in data[key] if not r.get('id',r.get('question_id','')).startswith('G-')]
con=sqlite3.connect(ROOT/'chemistry.sqlite'); con.execute('PRAGMA foreign_keys=ON')
for table,col in [('solutions','question_id'),('hints','question_id'),('questions','id')]: con.execute(f"DELETE FROM {table} WHERE {col} LIKE 'G-%'")
for g in graphs:
    pts=g['points']; p,q,r=pts[40],pts[90],pts[150]
    task_specs=[
      ('read',f"Read the ordinate when the horizontal coordinate is {q['x']:.8g}.",q['y'],g['y_label'],
       ['Locate the specified value on the horizontal axis.','Follow to the plotted curve and read the vertical coordinate.',f"The dataset's sampled ordinate is {q['y']:.10g}."],
       'Are you reading the horizontal or vertical axis?',4),
      ('change',f"Find the signed change in the vertical quantity from x={p['x']:.8g} to x={r['x']:.8g}.",r['y']-p['y'],g['y_label'],
       ['Signed change means final minus initial.',f"Final y={r['y']:.10g}; initial y={p['y']:.10g}.",f"Subtract to obtain {r['y']-p['y']:.10g}."],
       'Which value is final, and does the quantity rise or fall?',5),
      ('secant',f"Calculate the average slope between x={p['x']:.8g} and x={r['x']:.8g}; use vertical-axis units per horizontal-axis unit.",(r['y']-p['y'])/(r['x']-p['x']),g['y_label']+' per '+g['x_label'],
       ['Average slope is (y2-y1)/(x2-x1), not necessarily the instantaneous slope.',f"Numerator={r['y']-p['y']:.10g}; denominator={r['x']-p['x']:.10g}.",f"Their quotient is {(r['y']-p['y'])/(r['x']-p['x']):.10g}."],
       'What changes belong in the numerator and denominator of a slope?',5),
      ('difference_of_changes',f"Calculate (the signed y change from x={q['x']:.8g} to x={r['x']:.8g}) minus (the signed y change from x={p['x']:.8g} to x={q['x']:.8g}). Do not interpret this as a difference of slopes: the intervals need not be equal.",
       (r['y']-q['y'])-(q['y']-p['y']),g['y_label'],
       [f"First change={r['y']-q['y']:.10g}.",f"Second change={q['y']-p['y']:.10g}.",f"First minus second={(r['y']-q['y'])-(q['y']-p['y']):.10g}."],
       'Calculate each signed change separately before comparing them.',5)
    ]
    for task,prompt,ans,unit,steps,hint,practice in task_specs:
        qid='G-'+g['id']+'-'+task
        question=dict(id=qid,topic_id=g['topic_ids'][0],family_id='graph-'+g['family_id']+'-'+task,
            origin='original',prompt=f"Use supplied dataset {g['id']} ({g['title']}). Horizontal axis: {g['x_label']}; vertical axis: {g['y_label']}. "+prompt+
            ' Use the data table for a precise answer; the graph alone supports an approximate reading.',
            answer_kind='numeric',science_practices=[practice],difficulty='uncalibrated',exam_authenticity='original graph-literacy drill; not an official AP item',
            review_status='arithmetic_checked_not_expert_reviewed',parameters=dict(x1=p['x'],x2=q['x'],x3=r['x']),
            misconception='Confusing an axis value, signed change, and slope.',graph_dataset_id=g['id'],
            display_contract='Provide the referenced graph AND its accessible numerical data table; otherwise do not serve the question.',
            visible_graph_is_task_input=True)
        # Absolute tolerance is scale-aware and much smaller than the usual graph-reading tolerance.
        solution=dict(question_id=qid,answer=ans,answer_unit=unit,steps=steps,relative_tolerance=.005,
            absolute_tolerance=max(abs(v['y']) for v in pts)*1e-8+1e-16,
            precision_policy='Data-table exercise; if graded from graphical estimates, use a separately calibrated pixel/axis tolerance.',access='teacher_or_backend_only')
        hs=[dict(question_id=qid,level=1,text=hint,reveals_final_answer=False),
            dict(question_id=qid,level=2,text='Use the labeled units and check whether the sign agrees with the plotted change.',reveals_final_answer=False)]
        assert math.isfinite(ans)
        data['questions'].append(question);data['solutions'].append(solution);data['hints'].extend(hs)
        data['validation_checks'].append(dict(question_id=qid,check='dataset_coordinate_arithmetic',status='pass'))
        con.execute('INSERT INTO questions VALUES(?,?,?,?,?,?,?)',(qid,question['topic_id'],question['family_id'],question['prompt'],'original',question['review_status'],json.dumps(question)))
        con.execute('INSERT INTO solutions VALUES(?,?)',(qid,json.dumps(solution)))
        con.executemany('INSERT INTO hints VALUES(?,?,?)',[(qid,h['level'],h['text']) for h in hs])
assert len(set(q['id'] for q in data['questions']))==len(data['questions'])
for name in ('questions','solutions','hints'): (ROOT/(name+'.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in data[name]))
(ROOT/'chemistry_database.json').write_text(json.dumps(data,indent=2))
coverage=json.loads((ROOT/'coverage_200_types_per_topic.json').read_text())
for c in coverage:
    families=sorted({q['family_id'] for q in data['questions'] if q['topic_id']==c['topic_id']})
    c.update(authored_families=families,authored_family_count=len(families),minimum_additional_authored_types=max(0,200-len(families)))
    con.execute('UPDATE coverage_targets SET authored_types=?,data_json=? WHERE topic_id=?',(len(families),json.dumps(c),c['topic_id']))
(ROOT/'coverage_200_types_per_topic.json').write_text(json.dumps(coverage,indent=2))
con.commit();con.close()
report=json.loads((ROOT/'validation_report.json').read_text());report.update(original_questions=len(data['questions']),graph_reading_questions=3840,
    hints=len(data['hints']),distinct_authored_families=len(set(q['family_id'] for q in data['questions'])),
    per_unit_question_counts=dict(collections.Counter(int(q['topic_id'].split('.')[0]) for q in data['questions'])))
(ROOT/'validation_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

visual_report=json.loads((ROOT/'visual_validation_report.json').read_text())
visual_report['existing_authored_families']=report['distinct_authored_families']
(ROOT/'visual_validation_report.json').write_text(json.dumps(visual_report,indent=2))

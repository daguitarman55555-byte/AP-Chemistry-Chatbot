from pathlib import Path
import json
P=Path(__file__).resolve().parent;d=json.loads((P/'chemistry_database.json').read_text());ss={s['question_id']:s for s in d['solutions']}
lines=['# Curriculum map','', '91 numbered topics, original seed explanations. This is a topic-level index, not complete learning-objective coverage.','']
for u in d['units']:
    lines+=['## Unit '+str(u['id'])+': '+u['title'],'']
    for t in d['topics']:
        if t['unit_id']==u['id']:lines+=['### '+t['id']+' — '+t['label'],'',ss['C-'+t['id']]['answer'],'']
(P/'CURRICULUM_MAP.md').write_text('\n'.join(lines))
lines=['# Worked examples','', 'Original numerical models. Teacher/backend reference: these contain answers.',''];seen=set()
for q in d['questions']:
    if q['answer_kind']=='numeric' and not q['id'].startswith('G-') and q['family_id'] not in seen:
        seen.add(q['family_id']);lines+=['## '+q['family_id'].replace('_',' '),'',q['prompt'],'']
        lines += [str(i)+'. '+s for i,s in enumerate(ss[q['id']]['steps'],1)]+['']
(P/'WORKED_EXAMPLES.md').write_text('\n'.join(lines))
rows=[json.loads(s) for s in (P/'graph_datasets.jsonl').read_text().splitlines()]
thin=[{k:r[k] for k in ['id','family_id','title','x_label','y_label','points','parameters','equation','assumptions']} for r in rows]
payload=json.dumps(thin,separators=(',',':')).replace('</','<\\/')
(P/'graph_explorer.html').write_text((P/'graph_viewer_template.html').read_text().replace('__GRAPH_DATA__',payload))
print('Built curriculum map, worked examples, and offline interactive graph explorer.')

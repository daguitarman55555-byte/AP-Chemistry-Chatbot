"""Minimal server-side visual payload gate; not a complete access-control service."""
import math
def make_visual_payload(dataset, *, purpose, approved_stimulus_ids=()):
    if purpose not in {'exploration','question_stimulus'}:
        raise ValueError('Unsupported purpose; hidden solutions cannot be rendered through this route')
    if purpose=='question_stimulus' and dataset['id'] not in approved_stimulus_ids:
        raise PermissionError('Task author has not approved this curve as visible input')
    points=dataset['points']
    if not 2<=len(points)<=5000:raise ValueError('Point count outside renderer bounds')
    if any(not math.isfinite(p[k]) for p in points for k in ('x','y')):raise ValueError('Non-finite coordinate')
    if any(a['x']>=b['x'] for a,b in zip(points,points[1:])):raise ValueError('Horizontal values must increase')
    return dict(type='cartesian_curve',dataset_id=dataset['id'],title=dataset['title'],
        x_label=dataset['x_label'],y_label=dataset['y_label'],points=[dict(x=p['x'],y=p['y']) for p in points],
        provenance=dataset['provenance'],assumptions=dataset['assumptions'],
        controls=['inspect_point'],accessible_alternative='data_table')

if __name__=='__main__':
    import json
    from pathlib import Path
    p=Path(__file__).resolve().parent
    row=json.loads((p/'graph_datasets.jsonl').read_text().splitlines()[0])
    out=make_visual_payload(row,purpose='exploration');assert 'equation' not in out and 'parameters' not in out
    try:make_visual_payload(row,purpose='question_stimulus')
    except PermissionError:pass
    else:raise AssertionError('Unapproved stimulus leaked')
    out=make_visual_payload(row,purpose='question_stimulus',approved_stimulus_ids=[row['id']]);assert out['points']
    print('Visual gate checks passed: explicit stimulus approval required; model parameters omitted.')

"""Offline deterministic practice runner, not an LLM or general chemistry grader."""
import argparse
import json
import math
import re
import sqlite3
from pathlib import Path

NUMBER=re.compile(r'^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$')

class TutorSession:
    def __init__(self, question, solution, hints):
        self._question=question
        self._solution=solution
        self._hints=[h['text'] for h in sorted(hints,key=lambda h:h['level'])]
        self._attempts=0
        self._hint_index=0
        self._last_hint_attempt=-1
        self._complete=False

    def prompt(self):
        return {k:self._question[k] for k in ('id','topic_id','prompt')}

    def hint(self):
        if self._complete:return {'status':'complete','message':'You have already completed this item.'}
        if self._last_hint_attempt==self._attempts:
            return {'status':'attempt_needed','message':'Try a step before requesting another hint.'}
        if self._hint_index>=len(self._hints):
            return {'status':'prerequisite_needed','message':'The prepared hints are exhausted. Review the relevant principle with a teacher; the solution remains hidden.'}
        text=self._hints[self._hint_index]
        self._hint_index+=1;self._last_hint_attempt=self._attempts
        return {'status':'hint','level':self._hint_index,'message':text}

    def submit(self, text, unit=None):
        if self._complete:return {'status':'complete','message':'You have already completed this item.'}
        text=str(text).strip()
        if not text:return {'status':'empty','message':'Enter your attempt first.'}
        if self._question['answer_kind']!='numeric':
            self._attempts+=1
            return {'status':'review_needed','message':'Your explanation needs human review. This prototype cannot reliably grade written chemistry reasoning.'}
        if len(text)>100 or not NUMBER.fullmatch(text):
            return {'status':'invalid_number','message':'Enter a finite number; scientific notation such as 2.5e-3 is accepted. Expressions are not executed.'}
        value=float(text)
        if not math.isfinite(value):return {'status':'invalid_number','message':'Enter a finite number.'}
        self._attempts+=1
        expected_unit=self._solution.get('answer_unit')
        if expected_unit and expected_unit!='dimensionless' and unit!=expected_unit:
            return {'status':'units_needed','message':f'Use the requested unit: {expected_unit}. Unit conversion is not implemented in this prototype.'}
        correct=math.isclose(value,self._solution['answer'],rel_tol=self._solution.get('relative_tolerance') or 0,
                            abs_tol=self._solution.get('absolute_tolerance') or 0)
        if correct:
            self._complete=True
            return {'status':'correct','message':'Your numerical result matches within the current tolerance. Explain your method and check significant figures.'}
        return {'status':'try_again','message':'That result does not match. Check the setup, units, and arithmetic; you can request the next hint.'}

def load_session(db_path, question_id=None, topic=None):
    with sqlite3.connect(db_path) as con:
        if question_id:
            row=con.execute('SELECT data_json FROM questions WHERE id=?',(question_id,)).fetchone()
        elif topic:
            row=con.execute("SELECT data_json FROM questions WHERE topic_id=? AND origin='original' AND id NOT LIKE 'G-%' ORDER BY CASE WHEN id LIKE 'C-%' THEN 1 ELSE 0 END,id LIMIT 1",(topic,)).fetchone()
        else:raise ValueError('Specify a question or topic')
        if not row:raise ValueError('No matching question')
        question=json.loads(row[0])
        if question.get('graph_dataset_id'):raise ValueError('Graph tasks require a graph and data-table renderer; unavailable in the terminal runner')
        solution=json.loads(con.execute('SELECT data_json FROM solutions WHERE question_id=?',(question['id'],)).fetchone()[0])
        hints=[dict(level=r[0],text=r[1]) for r in con.execute('SELECT level,text FROM hints WHERE question_id=? ORDER BY level',(question['id'],))]
    return TutorSession(question,solution,hints)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--question');group.add_argument('--topic')
    args=parser.parse_args();db=Path(__file__).resolve().parent/'corpus'/'chemistry.sqlite'
    if not db.exists():parser.error('Run python corpus/rebuild_all.py first')
    try:session=load_session(db,args.question,args.topic)
    except ValueError as e:parser.error(str(e))
    print(session.prompt()['prompt']);print('Enter hint, quit, or your attempt. For numeric answers use number | unit, for example: 0.20 | mol')
    while True:
        try:text=input('> ').strip()
        except (EOFError,KeyboardInterrupt):print();break
        if text.lower()=='quit':break
        if text.lower()=='hint':response=session.hint()
        else:
            parts=text.split('|',1);response=session.submit(parts[0],parts[1].strip() if len(parts)>1 else None)
        print(response['message'])
        if response['status']=='correct':break

if __name__=='__main__':main()

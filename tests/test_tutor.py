import unittest
from tutor import TutorSession

class TutorTests(unittest.TestCase):
    def session(self):
        return TutorSession({'id':'test','topic_id':'1.1','prompt':'Find the amount.','answer_kind':'numeric'},
            {'answer':.25,'answer_unit':'mol','steps':['hidden'],'relative_tolerance':.005,'absolute_tolerance':1e-14},
            [{'level':1,'text':'Check the units.'},{'level':2,'text':'Convert mass to amount.'}])
    def test_prompt_omits_solution(self):
        self.assertEqual(set(self.session().prompt()),{'id','topic_id','prompt'})
    def test_hint_requires_intervening_attempt(self):
        s=self.session();self.assertEqual(s.hint()['status'],'hint');self.assertEqual(s.hint()['status'],'attempt_needed')
        s.submit('0.1','mol');self.assertEqual(s.hint()['level'],2)
    def test_nonfinite_and_expressions_rejected(self):
        for v in ['nan','inf','1e9999','1/4','__import__("os")']:
            self.assertEqual(self.session().submit(v,'mol')['status'],'invalid_number')
    def test_units_required(self):
        self.assertEqual(self.session().submit('.25','g')['status'],'units_needed')
    def test_correct_result_and_no_answer_field(self):
        response=self.session().submit('2.5e-1','mol');self.assertEqual(response['status'],'correct');self.assertNotIn('answer',response)
    def test_incorrect_does_not_reveal_result(self):
        response=self.session().submit('2','mol');self.assertEqual(response['status'],'try_again');self.assertNotIn('0.25',str(response))
    def test_explanation_is_not_falsely_graded(self):
        s=self.session();s._question['answer_kind']='explanation'
        self.assertEqual(s.submit('Because charge is conserved')['status'],'review_needed')
    def test_no_more_hints_after_completion(self):
        s=self.session();s.submit('.25','mol');self.assertEqual(s.hint()['status'],'complete')

if __name__=='__main__':unittest.main()

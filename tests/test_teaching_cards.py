import unittest
from chat_engine import Catalog, Conversation, Provider
from teaching_cards import CARDS, teaching_chunks

class TeachingCardsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.catalog=Catalog()
    def test_nine_units_and_unique_ids(self):
        cards=teaching_chunks(self.catalog.topic_map)
        self.assertEqual({c['topic_id'].split('.')[0] for c in cards},set('123456789'))
        self.assertEqual(len({c['id'] for c in cards}),9)
        for c in cards:
            self.assertEqual(len(c['guiding_questions']),2)
            self.assertEqual(c['review_status'],'authored_not_expert_reviewed')
    def test_all_cards_retrievable(self):
        for card in CARDS:
            with self.subTest(title=card[1]):
                hits=self.catalog.retrieve(card[2])
                self.assertIn(card[1],[h['title'] for h in hits])
    def test_offline_card_asks_question_not_solution(self):
        c=Conversation(self.catalog,Provider(key='',model=''))
        r=c.chat(CARDS[0][2])
        self.assertEqual(r['message'],CARDS[0][5])
        self.assertEqual(r['provider_calls'],0)

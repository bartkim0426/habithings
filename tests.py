import os
import json
import unittest
from unittest import TestCase
from unittest.mock import patch

import habitica

FAKE_DATA = os.path.join(os.path.dirname(__file__), 'fake-results.json')

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

class ThingsHabiticaTestCase(TestCase):
    def setUp(self):
       fake_data = json.loads(open(FAKE_DATA).read())
       self.create_success_data = fake_data.get('create_success_data')
       self.score_success_data = fake_data.get('score_success_data')

    @patch('habitica.create_habitica_task')
    def test_create_task(self, mock_create):
        mock_create.return_value = MockResponse(
            status_code=201,
            json_data=self.create_success_data,
        )
        content = 'test content'
        things_uuid = '3C162AC4-4629-489B-8587-C51E9C8A1A91'
        res = habitica.create_habitica_task(content, things_uuid)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json(), self.create_success_data)

    @patch('habitica.create_habitica_task')
    def test_get_task_id(self, mock_create):
        mock_create.return_value = MockResponse(
            status_code=201,
            json_data=self.create_success_data,
        )
        res = habitica.create_habitica_task('test')
        data = res.json()
        result = habitica.get_task_id(data)
        self.assertEqual(result, "1fdf8c4a-00dc-48ac-97fb-cedcdd041560")

    def test_execute_things_sqlite3(self):
        result = habitica.execute_things_sqilte3('select 1')
        self.assertEqual(result, [(1, )])
        
#     # TODO: mock Things.sqlite3 data from others
#     # TODO: mock Things.sqlite3 data -> 24 hour invalid for the days
#     @patch('habitica.THINGS_DB', './Things.sqlite3')
#     def test_select_all_things_tasks_24_hours(self):
#         result = habitica.select_all_things_24_hours()
#         self.assertEqual(len(result), 1)
# 
  # TODO: mock Things.sqlite3 data -> 24 hour invalid for the days
#     @patch('habitica.create_habitica_task')
#     def test_create_habitica_task_from_things(self, mock_create):
#         mock_create.return_value = MockResponse(
#             status_code=201,
#             json_data=self.create_success_data,
#         )
#         result = habitica.create_habitica_task_from_things()
#         self.assertEqual(len(result), 9)

    @patch('habitica.score_habitica_task_from_id')
    def test_score_habitica_task_from_id(self, mock_score):
        mock_score.return_value = MockResponse(
            status_code=200,
            json_data=self.score_success_data,
        )
        task_id = "1fdf8c4a-00dc-48ac-97fb-cedcdd041560"
        res = habitica.score_habitica_task_from_id(task_id)
        self.assertEqual(res.status_code, 200)

    def test_get_task_id_from_response(self):
        res = MockResponse(
            status_code=201,
            json_data=self.create_success_data,
        )
        result = habitica.get_task_id_from_response(res)
        self.assertEqual(result, "1fdf8c4a-00dc-48ac-97fb-cedcdd041560")

    @patch('habitica.score_habitica_task_from_id')
    @patch('habitica.create_habitica_task')
    @patch('habitica.THINGS_DB', './Things.sqlite3')
    def test_daily_create_and_score(self, mock_create, mock_score):
        mock_score.return_value = MockResponse(
            status_code=200,
            json_data=self.score_success_data,
        )
        mock_create.return_value = MockResponse(
            status_code=201,
            json_data=self.create_success_data,
        )
        result = habitica.daily_create_and_score()
        self.assertEqual(len(result), 0)
        # self.assertTrue(result[0].is_success)

    @patch('habitica.THINGS_DB', './Things.sqlite3')
    def test_select_things_by_date(self):
        start, end = '2020-01-01', '2020-06-10'
        result = habitica.select_things_by_date(start, end)
        self.assertEqual(len(result), 6)

    # TODO: select_things_by_date를 사용해서 habitica에 api 전송할 수 있게 (날짜 선택해서 해당 날짜만 create and score)
    @patch('habitica.score_habitica_task_from_id')
    @patch('habitica.create_habitica_task')
    @patch('habitica.THINGS_DB', './Things.sqlite3')
    def test_create_and_score_by_date(self, mock_create, mock_score):
        mock_score.return_value = MockResponse(
            status_code=200,
            json_data=self.score_success_data,
        )
        mock_create.return_value = MockResponse(
            status_code=201,
            json_data=self.create_success_data,
        )
        start, end = '2020-01-01', '2020-06-10'
        result = habitica.create_and_score_by_date(start, end)
        self.assertEqual(len(result), 6)

    @patch('habitica.score_habitica_task_from_id')
    @patch('habitica.create_habitica_task')
    @patch('habitica.THINGS_DB', './Things.sqlite3')
    def test_create_and_score(self, mock_create, mock_score):
        mock_score.return_value = MockResponse(
            status_code=200,
            json_data=self.score_success_data,
        )
        mock_create.return_value = MockResponse(
            status_code=201,
            json_data=self.create_success_data,
        )
        start, end = '2020-01-01', '2020-06-10'
        rows = habitica.select_things_by_date(start, end)
        result = habitica.create_and_score(rows)
        self.assertEqual(len(result), 6)

    # TODO: 일단정리해서 깃헙에 올리기
    # TODO: class refactoring
    # TODO: 혹은 이미 추가된 항목 validation


if __name__ == '__main__':
    unittest.main()

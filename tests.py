import os
import json
import unittest
import sqlite3
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


class ThingsDBTestCase(TestCase):
    @staticmethod
    def things_db():
        db = habitica.ThingsDB(database='./test.sqlite3')
        return db

    # def setUp(self):
        # self.db = habitica.ThingsDB()

    def test_connect(self):
        db = self.things_db()
        db.connect()
        self.assertIsInstance(db.cursor, sqlite3.Cursor)
        self.assertTrue(db.connected)

    def test_close_without_connect(self):
        db = self.things_db()
        db.close()
        self.assertFalse(db.connected)

    def test_close(self):
        db = self.things_db()
        db.connect()
        db.close()
        self.assertFalse(db.connected)

    def test_execute(self):
        db = self.things_db()
        db.connect()
        db.execute('select 1')
        self.assertTrue(db.connected)

    def test_get_rows(self):
        db = self.things_db()
        db.connect()
        result = db.get_rows('select 1')

        self.assertEqual(result, [(1,)])

    def test_get_complete_tasks_between(self):
        db = self.things_db()
        db.connect()
        start, end = '2020-01-01', '2020-06-10'
        result = db.get_complete_tasks_between(start, end)
        self.assertEqual(len(result), 6)


class HabiThingsTestCase(TestCase):
    def setUp(self):
        self.ht = habitica.HabiThings(db_path='./test.sqlite3')
        fake_data = json.loads(open(FAKE_DATA).read())
        self.create_success_data = fake_data.get('create_success_data')
        self.score_success_data = fake_data.get('score_success_data')

    def test_habi_things_class_init(self):
        self.assertTrue(self.ht.db.connected)

    def test_select_things_by_date(self):
        start, end = '2020-01-01', '2020-06-10'
        result = self.ht.select_things_by_date(start, end)
        self.assertEqual(len(result), 6)

    @patch('habitica.HabiThings.create_habitica_task')
    def test_create_task(self, mock_create):
        mock_create.return_value = MockResponse(
            status_code=201,
            json_data=self.create_success_data,
        )
        content = 'test content'
        things_uuid = '3C162AC4-4629-489B-8587-C51E9C8A1A91'
        res = self.ht.create_habitica_task(content, things_uuid)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json(), self.create_success_data)

    @patch('habitica.HabiThings.score_habitica_task_from_id')
    def test_score_habitica_task_from_id(self, mock_score):
        mock_score.return_value = MockResponse(
            status_code=200,
            json_data=self.score_success_data,
        )
        task_id = "1fdf8c4a-00dc-48ac-97fb-cedcdd041560"
        res = self.ht.score_habitica_task_from_id(task_id)

        self.assertEqual(res.status_code, 200)

    def test_get_task_id_from_response(self):
        res = MockResponse(
            status_code=201,
            json_data=self.create_success_data,
        )
        result = self.ht.get_task_id_from_response(res)

        self.assertEqual(result, "1fdf8c4a-00dc-48ac-97fb-cedcdd041560")

    @patch('habitica.HabiThings.score_habitica_task_from_id')
    @patch('habitica.HabiThings.create_habitica_task')
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
        rows = self.ht.select_things_by_date(start, end)
        result = self.ht.create_and_score(rows)

        self.assertEqual(len(result), 6)

    @patch('habitica.HabiThings.score_habitica_task_from_id')
    @patch('habitica.HabiThings.create_habitica_task')
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
        result = self.ht.create_and_score_by_date(start, end)
        self.assertEqual(len(result), 6)


if __name__ == '__main__':
    unittest.main()

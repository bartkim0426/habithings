import os
import time
import json
import sqlite3
from datetime import datetime, date
from dataclasses import dataclass

import httpx

HABITICA_API_USER = os.getenv('HABITICA_API_USER')
HABITICA_API_KEY = os.getenv('HABITICA_API_KEY')

# TODO: change to relative path
THINGS_DB = "/Users/seulchankim/Library/Containers/com.culturedcode.ThingsMac/Data/Library/Application Support/Cultured Code/Things/Things.sqlite3"
HABITICA_HEADERS = {
    "x-api-user": HABITICA_API_USER,
    "x-api-key": HABITICA_API_KEY,
    "Content-Type": "application/json",
}


@dataclass
class TaskResult:
    '''Class for return final result after create and score'''
    task_id: str
    content: str
    is_success: bool


class ThingsDB:
    '''
    DB initialize and execute Things3 SQLite3 database
    '''
    def __init__(self, database=THINGS_DB):
        self.database = database
        self.connection = None
        self.connected = False

    def connect(self):
        '''Connect to the SQLite3 database'''
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        self.connected = True

    def close(self):
        if not self.connection:
            return
        '''Close the SQLite3 database'''
        self.connection.commit()
        self.connection.close()
        self.connected = False

    def execute(self, query):
        # TODO: validation for only select
        self.cursor.execute(query)

    def get_rows(self, query):
        self.execute(query)
        return self.cursor.fetchall()

    def get_complete_tasks_between(self, start_date, end_date):
        start_timestamp = time.mktime(datetime.strptime(start_date, "%Y-%m-%d").timetuple())
        end_timestamp = time.mktime(datetime.strptime(end_date, "%Y-%m-%d").timetuple())
        query = f'''
        SELECT title, uuid
        FROM TMTask
        WHERE trashed = 0 AND type = 0
        AND status = 3
        AND stopDate >= {start_timestamp}
        ANd stopDate < {end_timestamp}
        '''
        return self.get_rows(query)


class HabiThings:
    '''
    Create and score Habitica task from Things 3 app sqilte db

    execute_things_sqlite3
    '''
    def __init__(self, db_path=THINGS_DB):
        self.db = ThingsDB(database=db_path)
        self.db.connect()

    def select_things_by_date(self, start_date: str, end_date=date.today().strftime('%Y-%m-%d')):
        '''
        start_time: %Y-%m-%d
        end_time: %Y-%m-%d
        '''
        return self.db.get_complete_tasks_between(start_date, end_date)

    def create_habitica_task(self, content: str, things_uuid: str):
        url = "https://habitica.com/api/v3/tasks/user"
        data = {
            "text": content,
            "type": "todo",
            "alias": f'task-from-things-{things_uuid}',
            "priority": 0.1,  # 0.1, 1, 1.5, 2
        }
        res = httpx.post(url, data=json.dumps(data), headers=HABITICA_HEADERS)
        return res

    def score_habitica_task_from_id(self, task_id: str):
        url = f'https://habitica.com/api/v3/tasks/{task_id}/score/up'
        res = httpx.post(url, headers=HABITICA_HEADERS)
        return res

    def get_task_id_from_response(self, create_response):
        try:
            assert create_response.status_code == 201
            result = create_response.json()
            assert result['success'] is True
        except AssertionError:
            # TODO: add logging
            print(create_response.json())
            return ''
        return result['data']['id']

    def create_and_score(self, things_rows: list) -> list:
        # TODO: change results to namedtuple
        results = []
        for row in things_rows:
            content, things_uuid = row[0:2]
            create_res = self.create_habitica_task(content, things_uuid)
            task_id = self.get_task_id_from_response(create_res)
            if task_id:
                score_res = self.score_habitica_task_from_id(task_id)
                is_score_success = score_res.json().get('success', False)
            else:
                is_score_success = False
            results.append(
                TaskResult(task_id, content, is_score_success)
            )
        return results

    def create_and_score_by_date(self, start_date: str, end_date=date.today().strftime('%Y-%m-%d')) -> list:
        things_rows = self.select_things_by_date(start_date, end_date)
        return self.create_and_score(things_rows)

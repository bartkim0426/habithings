import os
import time
import json
import sqlite3
from datetime import datetime, date, timedelta
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

def execute_things_sqilte3(query):
    # TODO: check sql file is exist first
    print(THINGS_DB)
    conn = sqlite3.connect(THINGS_DB)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows


# def select_all_things_24_hours():
#     query = '''
#     SELECT title, uuid
#     FROM TMTask
#     WHERE trashed = 0 AND type = 0
#     AND status = 3
#     AND stopDate > strftime('%s','now','-24 hours');
#     '''
#     data = execute_things_sqilte3(query)
#     return data


def get_task_id(data: dict):
    try:
        return data["data"]["_id"]
    except KeyError:
        return None


def create_habitica_task(content: str, things_uuid: str):
    url = "https://habitica.com/api/v3/tasks/user"
    data = {
        "text": content,
        "type": "todo",
        "alias": f'task-from-things-{things_uuid}',
        "priority": 0.1, # 0.1, 1, 1.5, 2
    }
    res = httpx.post(url, data=json.dumps(data), headers=HABITICA_HEADERS)
    return res


def score_habitica_task_from_id(task_id: str):
    url = f'https://habitica.com/api/v3/tasks/{task_id}/score/up'
    res = httpx.post(url, headers=HABITICA_HEADERS)
    return res


# def create_habitica_task_from_things() -> list:
#     things_rows = select_all_things_24_hours()
#     responses = []
#     for row in things_rows:
#         res = create_habitica_task(row[0])
#         responses.append(res)
#     return responses


def get_task_id_from_response(create_response):
    try:
        assert create_response.status_code == 201
        result = create_response.json()
        assert result['success'] == True
    except AssertionError:
        print(create_response.json())
        return ''
    return result['data']['id']


@dataclass
class TaskResult:
    '''Class for return final result after create and score'''
    task_id: str
    content: str
    is_success: bool
#     def print_total_result(self) -> str:
#         return f"{count(is_success}"

def mktime_from_string(date_str):
    return time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple())

def select_things_by_date(start_date: str, end_date=date.today().strftime('%Y-%m-%d')):
    '''
    start_time: %Y-%m-%d
    end_time: %Y-%m-%d
    '''
    # TODO: add validation for date format
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
    data = execute_things_sqilte3(query)
    return data


def create_and_score(things_rows: list) -> list:
    # TODO: change results to namedtuple
    results = []
    for row in things_rows:
        content, things_uuid = row[0:2]
        create_res = create_habitica_task(content, things_uuid)
        task_id = get_task_id_from_response(create_res)
        if task_id:
            score_res = score_habitica_task_from_id(task_id)
            is_score_success = score_res.json().get('success', False)
        else:
            is_score_success = False
        results.append(
            TaskResult(task_id, content, is_score_success)
        )
    return results


def create_and_score_by_date(start_date: str, end_date=date.today().strftime('%Y-%m-%d')) -> list:
    things_rows = select_things_by_date(start_date, end_date)
    return create_and_score(things_rows)


def daily_create_and_score():
    yesterday = datetime.strftime(date.today() - timedelta(days=1), '%Y-%m-%d')
    things_rows = select_things_by_date(yesterday)
    return create_and_score(things_rows)

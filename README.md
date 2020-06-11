# things habitica

[habitica v3 api](https://habitica.com/apidoc/)

# Usage

## Using pip

## Using with python code

### Add habitica user key and secret key for environment

TODO: add image for key

Edit habitica api key in `env` file (`vim env`)

```
export HABITICA_API_USER=<your_habitica_api_user>
export HABITICA_API_KEY=<user_habitica_api_key>
```

And source env file

```
$ source env
```

> Or you can just hard coding your key in `habitica.py`

### Execute command

```
python daily_create_and_score
```

## Function

### Mandatory
- [o] export Things3 to sqlite3
- [o] Create task from things from things3
- [o] Get task id from response
- [o] Bulk create task and return id from things3 file
- [o] Avoid duplication of same task for same content
- [o] Scoring task from taskid (or groupid)
- [o] Chnage export bases of things3 from 24h to something else -> based on date
- [ ] Refactor code to Class
- [ ] Packaging or dockerizing
- [ ] validation output for already used task

### Optional
- [ ] Get all task ids for tags?
- [ ] Move uncompleted task to habitica?
- [ ] Make backup file for Things3.sqlite before execute command

## Spec
- Python 3 (httpx)
- Mac OS
- crontab
- test code
- (optional) django or graphql

## 개발일지
- due date
  - 1차 개발은 6월 중순
  - 배포는 6월 말까지

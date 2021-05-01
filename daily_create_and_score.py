import habitica
from datetime import datetime, date, timedelta

hbthings = habitica.HabiThings()

print("-------------------------------------------------")
print(datetime.now())

# get tasks from the last day
tasks = hbthings.create_and_score_by_date(str(date.today() - timedelta(days = 3)))

for i in tasks:
    print(i)
print("-------------------------------------------------")
#!/usr/bin/python3

import sys
import random as rd
from tabulate import tabulate
from datetime import datetime
from datetime import date
from datetime import timedelta

n_weeks = 20
names = ["Anne-Sophie", "Li", "Claudia", "Jacob", "Mike", "Kai", "Haishan", "Charlotte", "Michael", "Thibault", "Daniel"]
bathrooms = [[0, 1, 2, 10], [3, 8, 9], [4, 5, 6, 7]]
tasks = ["Toilets", "Kitchen", "Trash (PET, paper)", "Trash (glass, metal)", "Floor"]
tasks.append("Trash bags")
first_day = (13, 1, 2020)

style = "plain"
if len(sys.argv) >= 2:
    style = str(sys.argv[1])

if len(sys.argv) >= 3:
    rd.seed(int(sys.argv[2]))

n_other_tasks = len(tasks)
n_bathrooms = len(bathrooms)
n_tasks = n_other_tasks + n_bathrooms
n_persons = len(names)

for i in range(n_bathrooms):
    rd.shuffle(bathrooms[i])

# Special constraint
while bathrooms[0][-1] != 0 or bathrooms[0][0] == 2: # Anne-Sophie last one and Claudia not first week
    rd.shuffle(bathrooms[0])

schedule = []

def special_constraint(i, person, s):
    if person == 7 and i < 3: # Lisa no floor first 2 weeks
        if 7 in s:
            s.remove(7) # Or is it 7?

def special_constraint_sort(i, p):
    if i < 3 and p == 0: # Anne-Sophie
        return 1000
    elif i == 0 and p == 2: # Claudia
        return 1000
    else:
        return 0

def count():
    # count[person][task] = number of this task, this person
    count = [[0 for _ in range(n_tasks)] for _ in names]
    for week in schedule:
        for i in range(n_tasks):
            count[week[i]][i] += 1
    return count

def get_tasks_mini(person, counter):
    c = counter[person][3:] # Not counting bathrooms
    m = min(c)
    M = max(c)
    assert M - m <= 1 # Invariant
    s = set()
    for i, n in enumerate(c):
        if n == m:
            s.add(i + n_bathrooms)
    return s

def worked_last_week(person):
    if len(schedule) >= 1:
        return person in schedule[-1]
    return False

def last_job(person):
    lj = -1
    i = len(schedule) - 1
    while i >= 0:
        if person in schedule[i]:
            lj = schedule[i].index(person)
            break
        i -= 1
    return {lj}

iterations = 0

def update(i):
    global schedule, iterations

    done = False

    while not done:
        iterations += 1
        week = [-1 for _ in range(n_tasks)]
        persons = set(range(n_persons))
        for (ib, b) in enumerate(bathrooms):
            ind = i % len(b)
            p = b[ind]
            week[ib] = p
            persons.remove(p)
        persons = list(persons)
        rd.shuffle(persons)
        c = count()
        persons.sort(key = lambda p: 2 * sum(c[p]) + worked_last_week(p) + special_constraint_sort(i, p)) # Priority to people with fewer jobs and who did pause
        avail_tasks = set(range(n_bathrooms, n_tasks))
        for p in persons[:len(avail_tasks)]:
            s = get_tasks_mini(p, c).intersection(avail_tasks) - last_job(p)
            special_constraint(i, p, s)
            if len(s) == 0:
                # print("Failure", i)
                return False
            task = rd.sample(s, 1)[0]
            avail_tasks.remove(task)
            week[task] = p
        schedule.append(week)
        if i + 1 < n_weeks:
            done = update(i + 1)
            if not done:
                schedule = schedule[:i]
        else:
            done = True
    return True

update(0)

weeks = []

def format_date(d):
    def f(x):
        return ("{:02d}".format(x))
    return f(d.day) + "/" + f(d.month)

d = date(first_day[2], first_day[1], first_day[0])

for i in range(n_weeks):
    d2 = d + timedelta(days=6)
    weeks.append(format_date(d) + " - " + format_date(d2))
    d = d + timedelta(days=7)
    i += 1

pretty_schedule = [[weeks[n]] + ["&nbsp;" + names[i] for i in week] for (n, week) in enumerate(schedule)]
headers = ["Weeks"] + ["Bathroom " + str(i + 1) for i in range(n_bathrooms)] + tasks

headers_plus = headers[:1]
pretty_schedule_plus = []

for i in range(n_tasks):
    h = headers[i + 1]
    headers_plus.append(h)
    headers_plus.append("✓")

for t in pretty_schedule:
    t_plus = t[:1]
    for i in range(n_tasks):
        t_plus.append(t[i + 1])
        t_plus.append('<input type="checkbox" style="pointer-events: none">')
    pretty_schedule_plus.append(t_plus)

print(tabulate(pretty_schedule_plus, headers=headers_plus, tablefmt=style))

if style == "plain":
    print("Number of jobs per person")
    c = count()
    for (p, name) in enumerate(names):
        print(name + ": " + str(sum(c[p])) + " jobs (" + str(sum(c[p][:n_bathrooms])) + " bathrooms)")

    print("Total number of iterations", iterations)

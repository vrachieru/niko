from sqlite3 import connect
from datetime import datetime
from operator import attrgetter
from collections import namedtuple
from itertools import groupby

# https://community.skype.com/t5/Linux/Skype-group-chat-not-working-anymore/td-p/3987288/page/4
# http://matthewmoisen.com/blog/programming/python/itertools-groupby-example/
# http://www.skillsyouneed.com/num/percent-change.html

database = connect('niko.db')
cursor = database.cursor()

Day    = namedtuple('Day',    ['date', 'score', 'mood', 'moods'])
Mood   = namedtuple('Mood',   ['smiley', 'people', 'percent'])
Entry  = namedtuple('Entry',  ['username', 'mood'])

Smiley = { -2 : ":'(", -1 : ":(", 0 : ":|", 1 : ":)", 2 : ":D" }


def getDates():
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT distinct entry_date
        FROM entries
        WHERE entry_date <> '%s'
        ORDER BY entry_date DESC
        LIMIT 2""" % today)

    return [entry[0] for entry in cursor.fetchall()]


def getDay(date):
    cursor.execute("""
        SELECT username, mood
        FROM entries
        INNER JOIN users
        ON entries.userid = users.id
        WHERE entries.entry_date = '%s'""" % date)

    entries = [Entry(*entry) for entry in cursor.fetchall()]
    grouped = groupby(sorted(entries, key=attrgetter('mood'), reverse=True), lambda entry: entry.mood)
    score   = sum(entry.mood for entry in entries) / len(entries)
    mood    = Smiley[round(score)]
    moods   = [getMood(moodId, group, len(entries)) for moodId, group in grouped]

    return Day(date, score, mood, moods)


def getMood(moodId, entry, totalEntries):
    group   = list(entry)
    smiley  = Smiley[moodId]
    people  = [g.username for g in group]
    percent = round(len(group)/totalEntries * 100, 1)

    return Mood(smiley, people, percent)


def getStatus():
    dates = getDates()
    if len(dates) == 0: return
    yesterday = getDay(dates[0])

    dayOfWeek = datetime.strptime(dates[0], "%Y-%m-%d").date().isoweekday()
    result = "The average team mood for %s was %s\n" % (('yesterday', 'Friday')[dayOfWeek == 5], yesterday.mood)

    if len(dates) == 2:
        dayBeforeYesterday = getDay(dates[1])
        trend   = ('decrease', 'increase')[yesterday.score > dayBeforeYesterday.score]
        percent = (dayBeforeYesterday.score - yesterday.score, yesterday.score - dayBeforeYesterday.score)[yesterday.score > dayBeforeYesterday.score] / dayBeforeYesterday.score * 100
        result += "There has been a mood %s of %.1f%% compared to the day before, for which the team mood was %s\n\n" % (trend, abs(percent), dayBeforeYesterday.mood)

    for mood in yesterday.moods:
        result += "%02.1f%% %s %s\n" % (mood.percent, mood.smiley, ', '.join(mood.people))

    return result

if __name__ == "__main__":
    print (getStatus())

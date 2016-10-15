from datetime import datetime
from operator import attrgetter
from collections import namedtuple
from itertools import groupby

from database import *
from utils import *

# https://community.skype.com/t5/Linux/Skype-group-chat-not-working-anymore/td-p/3987288/page/4
# http://matthewmoisen.com/blog/programming/python/itertools-groupby-example/
# http://www.skillsyouneed.com/num/percent-change.html

DayStatus = namedtuple('DayStatus',    ['date', 'score', 'mood', 'moods'])
MoodStatus = namedtuple('MoodStatus',   ['smiley', 'people', 'percent'])
UserMood = namedtuple('UserMood',  ['username', 'mood'])

def getLatestEntryDates(days=2):
    entries = selectAll('SELECT distinct entry_date FROM entries WHERE entry_date <> ? ORDER BY entry_date DESC LIMIT ?', (today(), days))
    return [entry[0] for entry in entries]

def getDayStatus(date):
    entries = selectAll('SELECT username, mood FROM entries INNER JOIN users ON entries.userid = users.id WHERE entries.entry_date = ?', (date,), UserMood)
    grouped = groupby(sorted(entries, key=attrgetter('mood'), reverse=True), lambda entry: entry.mood)
    score = sum(entry.mood for entry in entries) / len(entries)
    mood = getMoodSmileyByScore(round(score))
    moods = [getMoodStatus(moodId, group, len(entries)) for moodId, group in grouped]
    return DayStatus(date, score, mood, moods)

def getMoodStatus(moodId, entry, totalEntries):
    group = list(entry)
    smiley = getMoodSmileyByScore(moodId)
    people = [g.username for g in group]
    percent = round((len(group)/float(totalEntries)) * 100, 1)
    return MoodStatus(smiley, people, percent)

def getYesterdaysMood():
    return getDayMood(getLatestEntryDates(2))

def getDayMood(dates):
    if len(dates) == 0: return
    yesterday = getDayStatus(dates[0])

    dayOfWeek = datetime.strptime(dates[0], "%Y-%m-%d").date().isoweekday()
    result = "The average team mood for %s was %s\n" % (('yesterday', 'Friday')[dayOfWeek == 5], yesterday.mood)

    if len(dates) == 2:
        dayBeforeYesterday = getDayStatus(dates[1])
        trend   = ('decrease', 'increase')[yesterday.score > dayBeforeYesterday.score]
        percent = (dayBeforeYesterday.score - yesterday.score, yesterday.score - dayBeforeYesterday.score)[yesterday.score > dayBeforeYesterday.score] / dayBeforeYesterday.score * 100
        result += "There has been a mood %s of %.1f%% compared to the day before, for which the team mood was %s\n\n" % (trend, abs(percent), dayBeforeYesterday.mood)

    for mood in yesterday.moods:
        result += "%02.1f%% %s %s\n" % (mood.percent, mood.smiley, ', '.join(mood.people))

    return result


if __name__ == "__main__":
    print (getYesterdaysMood())

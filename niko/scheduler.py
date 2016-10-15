import datetime
import functools

from log import *

class Scheduler(object):
    def __init__(self):
        self.jobs = []

    def run_jobs(self):
        for job in self.jobs:
            if job.should_run():
                job.run()

    def every(self):
        job = Job()
        self.jobs.append(job)
        return job


class Job(object):
    def __init__(self):
        self.interval = None
        self.days = None
        self.time = None
        self.function = None
        self.last_run = None
        self.next_run = None

    def __repr__(self):
        def format(time):
            return time.strftime('%Y-%m-%d %H:%M:%S') if time else '[never]'

        function = self.function.__name__ if hasattr(self.function, '__name__') else repr(self.function)        
        args = [repr(x) for x in self.function.args]
        action = function + '(' + ', '.join(args) + ')'
        runtimes = '(last run: %s, next run: %s)' % (format(self.last_run), format(self.next_run))

        return '%s %s' % (action, runtimes)


    def workday(self):
        self.days = [1, 2, 3, 4, 5]
        self.interval = datetime.timedelta(days=1)
        return self

    def at(self, time_str):
        hour, minute = time_str.split(':')
        self.time = datetime.time(int(hour), int(minute))
        self.schedule_next_run()
        return self

    def do(self, function, *args):
        self.function = functools.partial(function, *args)
        return self

    def should_run(self):
        return datetime.datetime.now() >= self.next_run

    def run(self):
        LOGGER.info('Running job %s' % self)
        self.function()
        self.last_run = datetime.datetime.now()
        self.schedule_next_run()

    def schedule_next_run(self):
        now = datetime.datetime.now()
        if not self.next_run:
            self.next_run = now.replace(hour = self.time.hour, minute = self.time.minute, second = 0, microsecond = 0)
            if self.time < now.time():
                self.next_run += self.interval
        else:
            self.next_run += self.interval


scheduler = Scheduler()
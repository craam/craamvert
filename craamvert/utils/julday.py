from datetime import datetime, timedelta


def time(jd):
    return str((datetime(2001, 1, 1) + timedelta(seconds=jd)).time())


def date(jd):
    return str((datetime(2001, 1, 1) + timedelta(seconds=jd)).date())


def sec(sec):
    # return timedelta(seconds=sec).seconds * 1000
    return timedelta(seconds=sec).seconds

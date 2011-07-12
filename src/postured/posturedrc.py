import datetime
import os
import postured
import logging

class Options(object):
    minlength = datetime.timedelta(minutes=30)
    maxlength = datetime.timedelta(hours=2)

    starttime = datetime.time(hour=11)  # 11 am
    endtime = datetime.time(hour=19)    # 7 pm

    # days of the week (monday is 0 and sunday is 6)
    days = [0, 1, 2, 3, 4]              # M, Tu, W, Th, F 

    action = postured.actions.PlaySound()

    # this can either be "logging.DEBUG", "loggin.INFO", "logging.WARN", etc.
    loglevel = logging.DEBUG

    # whether or not to daemonize
    daemonize = False



opts = Options()


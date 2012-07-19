import datetime
import os
import postured
import logging

class Options(object):

    # The action will be run randomly sometime between minlength and
    # maxlength.  For instance, if minlength is 10 minutes, and maxlength
    # is 20 minutes, then the action will be ran sometime between 10 and
    # 20 minutes from now.
    minlength = datetime.timedelta(minutes=30)
    maxlength = datetime.timedelta(hours=2)

    # These are the bounds we want our action run by.  For example,
    # if start time is 11 am and endtime is 7 pm, then the action will
    # only be run between 11 am and 7 pm.  It will not be run at any other
    # time.  For instance, it may be run at 2pm, but it will not be run at
    # 9 pm.
    starttime = datetime.time(hour=11)  # 11 am
    endtime = datetime.time(hour=19)    # 7 pm

    # Like the previous bounds, this determines the days we will run our action.
    # For instance if days = [0, 1, 2, 3, 4], then our action will be run
    # Monday, Tuesday, Wednesday, Thursday, and Friday, but not Saturday and
    # Sunday.
    days = [0, 1, 2, 3, 4]              # M, Tu, W, Th, F

    # This is the action we want to take when the action is called.  The
    # action variable basically just needs to be an object that has a run()
    # method.  This run() method will be called when the action is run.
    action = postured.actions.PlaySound()

    # this can either be "logging.DEBUG", "loggin.INFO", "logging.WARN", etc.
    loglevel = logging.DEBUG

    # whether or not to daemonize
    daemonize = False

opts = Options()


#!/usr/bin/env python2

import imp
import sys
import os
import shutil
import time
import argparse
import logging
import logging.handlers

from datetime import datetime, timedelta
from random import random

from . import utils

logger = None

def importconfig(rcfile=None):
    """
    Try to import ~/.posturedrc, and if we can't find it,
    import posturedrc.py from within this module.
    """

    def importpyfile(name, path):
        """Import a python module from path and call it name."""
        try:
            return sys.modules[name]
        except KeyError:
            pass
        path = os.path.expanduser(path)
        with open(path, 'rb') as fp:
            return imp.load_module(name, fp, path, ('.py', 'rb', imp.PY_SOURCE))

    if rcfile is None:
        rcfile = "~/.posturedrc"

    # when we import the file from the home directory, we don't want to
    # create bytecode and clutter up the user's $HOME
    __old_write_val = sys.dont_write_bytecode
    sys.dont_write_bytecode = True

    try:
        # import our posturedrc file, if we can't find it, we can just create it
        posturedrc_mod = importpyfile("posturedrc", rcfile)
    except IOError as e:
        # TODO: This may not work if this program is being run from an egg, a zip, etc
        ex_posturedrc_path = os.path.join(os.path.dirname(__file__), "posturedrc.py")
        shutil.copy(ex_posturedrc_path, os.path.expanduser(rcfile))
        posturedrc_mod = importpyfile("posturedrc", rcfile)

    sys.dont_write_bytecode = __old_write_val

    return posturedrc_mod.opts


def nextaction(opts, count=0):
    """
    Check values from the config file, do the action if applicable, and return
    the number of seconds. Don't do the action if count is 0.
    """

    minlength, maxlength, starttime, endtime, days, curdate, curtime = checksettings(opts)

    difftime = maxlength - minlength
    newsecs = utils.tdtosecs(difftime) * random()
    newdelta = timedelta(seconds=newsecs) + minlength
    nexttime = datetime.today() + newdelta
    nextsecs = utils.tdtosecs(newdelta)

    logger.debug("current time: %s" % curtime)
    logger.debug("next alarm time: %s" % nexttime)

    if curtime < starttime:
        logger.info("curtime (%s) is before start time (%s), so not doing action." % 
                (curtime, starttime))
        return nextsecs
        
    if curtime > endtime:
        logger.info("curtime (%s) is after end time (%s), so not doing action" %
                (curtime, endtime))
        return nextsecs

    if curdate.weekday() not in days:
        logger.info("current day (%s) is not in days (%s), so not doing action" % 
                (utils.weekdaystr(curdate.weekday()), [utils.weekdaystr(day) for day in days]))
        return nextsecs

    if count <= 0:
        logger.debug("not doing action because count (%s) is less than 1" % count)
        return nextsecs

    logger.debug("running action...")
    opts.action.run()
    return nextsecs


def checksettings(opts):
    """
    Check that the settings values are all available and all make sense.
    Returns a tuple with minlength, maxlength, starttime, endtime, and days
    values from the config file, and the curtime and curdate.
    """
    def assert_hasattr(opts, varname):
        if not hasattr(opts, varname):
            logger.error("No \"%s\" defined in config." % varname)
            sys.exit(1)
    assert_hasattr(opts, "minlength")
    assert_hasattr(opts, "maxlength")
    assert_hasattr(opts, "starttime")
    assert_hasattr(opts, "endtime")
    assert_hasattr(opts, "days")
    assert_hasattr(opts, "action")

    minlength = opts.minlength
    maxlength = opts.maxlength
    starttime = opts.starttime
    endtime = opts.endtime
    days = opts.days

    # current time
    curdate = datetime.today()

    # time delta of zero
    tdzero = timedelta()
    curtime = curdate.time()


    if minlength > maxlength:
        logger.error("minlength %s cannot be greater than maxlength %s" % (minlength, maxlength))
        sys.exit(1)

    if minlength < tdzero: 
        logger.error("minlength %s cannot be less than 0" % minlength)
        sys.exit(1)

    if maxlength < tdzero: 
        logger.error("maxlength %s cannot be less than 0" % maxlength)
        sys.exit(1)

    if starttime >= endtime:
        logger.error("starttime %s is greater than or equal to endtime %s" % 
                (starttime, endtime))
        sys.exit(1)

    return minlength, maxlength, starttime, endtime, days, curdate, curtime

def daemonize_process():
    "Daemonize the process."
    if (hasattr(os, "devnull")):
        devnull = os.devnull
    else:
        devnull = "/dev/null"

    try: 
        pid = os.fork() 
        if pid > 0: 
            sys.exit(0) 
    except OSError, e: 
        logger.error("Error when forking first time: %s" % str(e))
        sys.exit(1) 
    
    os.chdir("/") 
    os.setsid() 
    os.umask(0) 
    
    try: 
        pid = os.fork() 
        if pid > 0: 
            sys.exit(0) 
    except OSError, e: 
        logger.error("Error when forking second time: %s" % str(e))
        sys.exit(1) 

    import resource     # Resource usage information.
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = MAXFD

    # Iterate through and close all file descriptors.
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:   # ERROR, fd wasn't open to begin with (ignored)
            pass

    os.open(devnull, os.O_RDWR) # standard input (0)
    os.dup2(0, 1)            # standard output (1)
    os.dup2(0, 2)            # standard error (2)


def is_daemon(opts, args):
    """
    Checks if should daemonize or not.  Command line arguments override the
    args from the config file.
    """
    if args.daemonize == True:
        daemonize = True
    elif args.daemonize == False:
        daemonize = False
    else:
        if not hasattr(opts, "daemonize"):
            print >> sys.stderr, "No \"daemonize\" defined in config."
            sys.exit(1)
        else:
            daemonize = opts.daemonize
    return daemonize

def setuplogging(opts, daemonize):
    global logger

    # make sure loglevel is defined in the config
    if not hasattr(opts, "loglevel"):
        print >> sys.stderr, "No \"loglevel\" defined in config."
        sys.exit(1)

    logger = logging.getLogger()
    logger.setLevel(opts.loglevel)

    if daemonize:
        sysloghandler = logging.handlers.SysLogHandler("/dev/log", "daemon")
        formatter = logging.Formatter("postured[%(process)d]: %(levelname)s: %(message)s")
        sysloghandler.setFormatter(formatter)
        logger.addHandler(sysloghandler)
    else:
        class InfoHigherFilter(logging.Filter):
            def filter(self, rec):
                return rec.levelno <= logging.INFO
        class WarnLowerFilter(logging.Filter):
            def filter(self, rec):
                return rec.levelno >= logging.WARN

        stdouthandler = logging.StreamHandler(sys.stdout)
        stdouthandler.setLevel(logging.DEBUG)
        stdouthandler.addFilter(InfoHigherFilter())
        logger.addHandler(stdouthandler)

        stderrhandler = logging.StreamHandler(sys.stderr)
        stderrhandler.setLevel(logging.WARNING)
        stderrhandler.addFilter(WarnLowerFilter())
        logger.addHandler(stderrhandler)


def main():

    parser = argparse.ArgumentParser(description="A cron-like reminder daemon.")

    parser.add_argument('--rcfile', '-i', action='store', 
            help="rc file (something other than ~/.posturedrc)")
    parser.add_argument('--verbose', '-v', action='store_true', 
            help="verbose output")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--daemonize', '--daemon', '-D', dest="daemonize", 
            action='store_true', default=None, help="detach from the controlling terminal")
    group.add_argument('--no-daemonize', '--no-daemon', '-N', dest="daemonize", 
            action='store_false', default=None, help="do not detach from the controlling terminal")

    args = parser.parse_args()

    # try to import the config file the user wants to use
    if args.rcfile:
        opts = importconfig(rcfile)
    else:
        opts = importconfig()

    daemonize = is_daemon(opts, args)
    setuplogging(opts, daemonize)

    if daemonize:
        logger.debug("Trying to daemonize...")
        daemonize_process()
        logger.debug("daemonized.")

    count = 0
    while True:
        sleeptime = nextaction(opts, count)
        time.sleep(sleeptime)
        count += 1

if __name__ == '__main__':
    main()


"""
Utility functions that can be used multiple places.
"""

from datetime import datetime, timedelta

def weekdaystr(day):
    """
    Convert an int day to a string representation of the day.
    For example, 0 returns "Monday" and 6 returns "Sunday".  This
    mirrors the way datetime.weekday() works.
    """
    if day < 0 or day > 6:
        raise ValueError("day is out of range")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[day]

def tdtosecs(td):
    """Convert a timedelta to seconds."""
    return (td.days * 24 * 60 * 60) + td.seconds + (td.microseconds * 0.000001)

def get_current_time():
    """
    Returns a tuple of the current date and the current time.
    """
    curdate = datetime.today()
    curtime = curdate.time()
    return curdate, curtime

def daemonize_process():
    "Daemonize the current process."
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

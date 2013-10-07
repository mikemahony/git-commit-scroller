#!/usr/bin/env python
# ---------------------------------------------------------------------------------------------
"""
"""
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------
import os, datetime, json, time
import pysvn, shutil
import smtplib
from threading import Lock

# ---------------------------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------------------------
REPO = 'https://github.com/mikemahony/git-commit-scroller'
LOCAL_TEMP_ROOT = '/tmp/xx/'
COMMIT_MAP = { '#':0, ' ':19 }
SVN_USER, SVN_PASS = 'mikemahony', 'P@55w0rd!'

# ---------------------------------------------------------------------------------------------
# POW!
# ---------------------------------------------------------------------------------------------
#####                 #   #                       # #### #    # #             
#####       ###        # #      #  #      #  #     # ## #    #####    # # # # 
#####    # ##### #    #####     ####     ######   ######## # # # # #   #####  
#####    ### # ###  ### # ###  # ## #   #  ##  #  #  ##  # #########  #  #  # 
#####    # ##### #  # ##### # ########  ########    #  #   ######### #########
#####    #  # #  #     # #    # #  # #  # #  # #   #    #  #  ###  # # #   # #
#####   ##       ##   #   #   #  ##  # ##  ##  ##   #  #   ## # # ##    # #   
def run(now):
    print 'Running for:', now

    ## Make sunday 0 and saturday 6
    today_weekday = (now.weekday() + 1 ) % 7  
    ## Make weeks start on Sundays
    today_week = now.isocalendar()[1] if not today_weekday == 0 else now.isocalendar()[1] + 1
    data = {}

    print today_week, today_weekday

    def login(*args):
        return True, SVN_USER, SVN_PASS, False

    c = pysvn.Client()
    c.callback_get_login = login

    print 'removing previous tmp root', LOCAL_TEMP_ROOT
    shutil.rmtree(LOCAL_TEMP_ROOT, ignore_errors=True)

    print 'checking out code'
    c.checkout(url=REPO, path=LOCAL_TEMP_ROOT)

    with open("%s/trunk/data.json" % LOCAL_TEMP_ROOT, 'r') as f:
        ## Read our persistant data
        data = json.load(f)

    if not 'start_week' in data:
        if today_weekday != 0:
            print "We haven't started yet and it ain't a Sunday, waiting until it is."
            exit()  
        else:
            data['start_week'] = today_week

    row = today_weekday
    column = today_week - data['start_week']

    try:
        c.add(path='%s/trunk/log.txt' % LOCAL_TEMP_ROOT)
    except pysvn._pysvn_2_6.ClientError:
        pass

    print '[%s][%s]:[%s]' % (row, column, data['drawing'][row][column])
    for i in range(COMMIT_MAP[data['drawing'][row][column]]):
        with open('%s/trunk/log.txt' % LOCAL_TEMP_ROOT, 'a') as s:
            s.write('%s,%s,%s\n' % (today_week, today_weekday, i))
        print 'checkin:', i
        c.checkin(path='%s/trunk/log.txt' % LOCAL_TEMP_ROOT, log_message="Auto-commit: %s,%s,%s" % (today_week, today_weekday, i))

    data['last_run'] = '%s/%s' % (today_week, today_weekday)

    with open("%s/trunk/data.json" % LOCAL_TEMP_ROOT, 'w') as f:
        ## Update our persistant data
        print 'dumping data as json to file:', data
        json.dump(data, f)
    c.checkin(path='%s/trunk/data.json' % LOCAL_TEMP_ROOT, log_message="Auto-commit: Updated variables")

if __name__ == "__main__":
    now = datetime.datetime.now()
    # now = datetime.datetime(2013, 9, 28, 1, 0, 0)
    try:
        run(now)
    except Exception, e:
        s = smtplib.SMTP('localhost')
        s.sendmail('mikem@animationmentor.com', ['mikemahony+gitcommitscroller@gmail.com'], 'git-commit-scroller failed! Error is: %s' % str(e))
        s.quit()

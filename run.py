#!/usr/bin/env python
# ---------------------------------------------------------------------------------------------
"""
"""
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------------
import os, datetime, json
import pysvn

# ---------------------------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------------------------
REPO = 'https://github.com/mikemahony/git-commit-scroller'
LOCAL_TEMP_ROOT = '/tmp/xx/'
COMMIT_MAP = { '#':0, ' ':20 }

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

    c = pysvn.Client()
    c.checkout(url=REPO, path=LOCAL_TEMP_ROOT)
    c.update(path=LOCAL_TEMP_ROOT)

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

    print '[%s][%s]:[%s]' % (row, column, data['drawing'][row][column])
    with open('%s/trunk/log.txt' % LOCAL_TEMP_ROOT, 'a') as s:
        for i in range(COMMIT_MAP[data['drawing'][row][column]]):
            print 'commit:', i
            s.write('%s,%s,%s\n' % (today_week, today_weekday, i))
            c.checkin(path=LOCAL_TEMP_ROOT, log_message="Auto-commit: %s,%s,%s" % (today_week, today_weekday, i))

    with open("%s/trunk/data.json" % LOCAL_TEMP_ROOT, 'w') as f:
        ## Update our persistant data
        json.dump(data, f)
        c.checkin(path=LOCAL_TEMP_ROOT, log_message="Updated variables")

if __name__ == "__main__":
    now = datetime.datetime.now()
    # now = datetime.datetime(2013, 9, 28, 1, 0, 0)
    run(now)

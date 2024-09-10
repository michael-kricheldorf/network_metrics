#!/usr/bin/env python3

'''imports'''
import time
import datetime
import sqlite3
import io
import sys
import os
import re
import json
import threading
import subprocess

'''
params:
    db          sql database connection
    intf_list   list of interface names to read from

 returns:
    0 when exited successfully, -1 and error message otherwise
'''
def read_dev(db, intf_list):
    dt = datetime.datetime.now(datetime.timezone.utc)

    dev_out = open("/proc/net/dev", mode='r').readlines()
    for line in dev_out[2:]:
        for intf in intf_list:
            if intf in line:
                return_string = "INSERT INTO {0} VALUES ('{1}', '{2}', {3}, {4});".format(
                    table_name, 
                    dt.strftime("%Y-%m-%d %H:%M:%S"), 
                    intf,
                    float(line[line.index(":")+1:].split()[0]),
                    float(line[line.index(":")+1:].split()[8]))
                print(return_string)
                db.execute(return_string)
                db.commit()
    return

'''init'''
# initialize paths
script_path = os.path.abspath(os.path.dirname(__file__))
# db_name = "/throughput_log.db"
# db_path = script_path + db_name
db_path = "/var/log/network_metrics/throughput_log.db"
table_name = "throughput"
interface_list = ["tnc0", "nebula1", "enp2s0"]

# connect to SQL database
try:
    con = sqlite3.connect(db_path, check_same_thread=False)
except:
    print("Could not find " + db_path + ". Exiting program.")
    sys.exit(1)
cur = con.cursor()

# create table if it doesn't already exist
cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{0}';".format(table_name))
if (cur.fetchone()[0] == 0):
    cur = con.execute("CREATE TABLE {0}(DATETIME TEXT, INTERFACE TEXT, RX INTEGER, TX INTEGER);".format(table_name))

while True:
    read_dev(con, interface_list)
    time.sleep(5)
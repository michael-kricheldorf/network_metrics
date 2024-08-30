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
import subprocess

'''
function to ping and read from `/proc/net/dev` continuously

params:
    db      sql database connection
    a       host alias
    n       interface
    addr    IP address
    pl      size of payload (bytes)
    to      timeout (sec)
    i       interval (sec)
'''
def ping(db, a, n, addr, pl, to):    
    # ping 
    dt = datetime.datetime.now(datetime.timezone.utc)
    res = subprocess.Popen(["ping", addr, "-c 1", "-I" + n, "-s" + str(pl),"-W" + str(to)], stdout=subprocess.PIPE)
    res_str = res.stdout.read().decode('utf-8')
    try:
        l_ms = float(re.search(r"time=(\d+\.*\d*) ms", res_str).group(1))
    
    except AttributeError:
        l_ms = -1

    # generate return string
    return_string = "INSERT INTO {0} VALUES ('{1}', '{2}', '{3}', '{4}', {5}, {6}, {7});".format(
                    table_name, dt.strftime("%Y-%m-%d %H:%M:%S"), a, n, addr, pl, to, l_ms)
    print(return_string)

    db.execute(return_string)
    db.commit()

    return

'''init'''
# initialize paths
script_path = os.path.abspath(os.path.dirname(__file__))
config_path = script_path + "/ping_config.json"
db_name = "/ping_log.db"
db_path = script_path + db_name
table_name = "latency"

latency_pattern = r'time=(\d+) ms'

'''meat'''

# load JSON config file
config = {}
try:
    with open(config_path, 'r') as file:
        config = json.load(file)
except:
    print("Error opening JSON file: ", config_path)

# load SQL database
try:
    con = sqlite3.connect(db_path)
except:
    print("Could not find " + db_path + ". Creating '" + db_name + "' in this directory.")
    f = open(db_name, "x")
    f.close()
    con = sqlite3.connect(db_name)
cur = con.cursor()

# create table if it doesn't already exist
cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{0}';".format(table_name))
if (cur.fetchone()[0] == 0):
    cur = con.execute("CREATE TABLE {0}(DATETIME TEXT, ALIAS TEXT, INTERFACE TEXT, ADDRESS TEXT, PL_SIZE INT, TIMEOUT_S INT, LATENCY_MS REAL);".format(table_name))

while True:
    for entry in config['addresses']:
        # get properties of each ping destination
        alias = entry['alias']
        interface = entry['interface']
        address = entry['address']
        pl_size = entry['pl_size']
        timeout = entry["timeout"]
        interval = entry["interval"]

        ping(con, alias, interface, address, pl_size, timeout)
        # interval doesn't really work as intended but that's okay
        time.sleep(interval)

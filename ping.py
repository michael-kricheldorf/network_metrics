#!/usr/bin/env python3

import pythonping
import time
import datetime
import sqlite3
import io
import sys
import os
import re
import json

script_path = "/home/ubuntu/miscellaneous/network_metrics/"

config_filename = script_path + "ping_config.json"

database_filename = ""
table_name = ""

# Create dictionary from JSON config file
config = {}

try:
    with open(config_filename, 'r') as file:
        config = json.load(file)

        database_filename = config['database']
        table_name = config['table']

except:
    print("Error opening JSON file")

# connect to SQL database
con = sqlite3.connect(database_filename)
cur = con.cursor()

# create table if it doesn't already exist
cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{0}';".format(table_name))
if (cur.fetchone()[0] == 0):
    cur = con.execute("CREATE TABLE {0}(DATETIME TEXT, ALIAS TEXT, I_TYPE TEXT, ADDRESS TEXT, INTERVAL_S REAL, PINGNO INT, PINGCOUNT INT, PAYLOAD_SIZE INT, TIMEOUT INT, LATENCY_MS REAL);".format(table_name))

for entry in config['addresses']:
    alias = entry['alias']
    i_type = entry['type']
    address = entry['address']
    
    for setting in entry['settings']:
        payload_size = setting['payload_size']
        ping_count = setting['ping_count']
        timeout_after = setting['timeout_after']
        interval = setting['interval']

        for ping_no in range(ping_count):
            # collect current datetime 
            t = datetime.datetime.now(datetime.timezone.utc)

            # change stdout to be StringIO object
            output = io.StringIO()
            sys.stdout = output

            pythonping.ping(address, verbose=True, count=1, out=output)

            output_lines = output.getvalue().splitlines()

            sys.stdout = sys.__stdout__

            for line in output_lines:
                # set the SQL insert value to default
                if (re.search("Round Trip Times", line) == None):
                    if (re.search("Request timed out", line) != None):
                        latency_ms = -1.0
        
                    elif (re.search("Reply from", line) != None):
                        latency_ms = re.findall(r'(\d+\.\d+)ms', line)[0]

                    return_string = "INSERT INTO {0} VALUES ('{1}', '{2}', '{3}', '{4}', {5}, {6}, {7}, {8}, {9}, {10});".format(
                        table_name, t.strftime("%Y-%m-%d %H:%M:%S"), alias, i_type, address, interval, ping_no, ping_count, payload_size, timeout_after, latency_ms)
                    print(return_string)   
                    cur = con.execute(return_string)
                    con.commit()
                else:
                    print(f"unhandled 'ping' response: {line}")

            time.sleep(interval)
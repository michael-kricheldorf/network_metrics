#!/usr/bin/env python3

'''
Michael Kricheldorf

This code heavily copies the functions found in the `atinout.c` program
written by Håkon Løvdal (hlovdal@users.sourceforge.net)
https://atinout.sourceforge.net/

TODO: split each cmd into its own table
TODO: add cmd line support for changing device port, e.g. /dev/ttyUSB0
'''

'''imports'''
import serial
import time
import datetime
import os
import sqlite3
import json

'''functions'''
def split_response(r):
    spl = r.split('\n')
    j = 0
    for i in range(len(spl)):
        i = i-j
        spl[i] = spl[i].rstrip()
        if spl[i] == '':
            spl.remove(spl[i])
            j += 1
    return spl

def re_find(a, b):
    return a.find(b) != -1

def is_final_result(r):
    if (r == ''):
        return False

    if (re_find(r, "OK") or re_find(r, "+CME_ERROR") or re_find(r, "+CMS ERROR") or re_find(r, "BUSY") or re_find(r, "ERROR") or re_find(r, "NO ANSWER") or re_find(r, "NO CARRIER") or re_find(r, "NO DIALTONE")):
        return True
    return False

'''init'''
script_path = os.path.abspath(os.path.dirname(__file__))
config_path = script_path + "/modem_config.json"

# load JSON config file
config = {}
try:
    with open(config_path, 'r') as file:
        config = json.load(file)
except:
    print("Error opening JSON file: ", config_path)

# load SQL database and tables
db_name = config['db_name']
db_path = script_path + db_name
try:
    con = sqlite3.connect(db_path, check_same_thread=False)
except:
    print("Could not find " + db_path + ". Creating '" + db_name + "' in this directory.")
    f = open(db_name, "x")
    f.close()
    con = sqlite3.connect(db_name, check_same_thread=False)
cur = con.cursor()

for entry in config['commands']:
    # create table if it doesn't already exist
    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{0}';".format(entry['table']))
    if (cur.fetchone()[0] == 0):
        cur = con.execute("CREATE TABLE {0}(DATETIME text, COMMAND text, RESPONSE text);".format(entry['table']))

# setup modem serial comm
modem = serial.Serial(port=config['port'], baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=False, rtscts=False, dsrdtr=False)

'''main'''
while True:
    for entry in config['commands']:
        cmd = entry['command']
        table = entry['table']
        # write and read AT commands
        response = ""
        cmd += "\r"
        modem.write(cmd.encode())
        while True:
            response += modem.read(1024).decode()
            if (is_final_result(response)):
                break

        # split response into first and second values (as far as I know, no other values are needed for now)
        spl = split_response(response)

        spl_cmd = spl[0]
        spl_resp = spl[1]

        # collect current datetime 
        t = datetime.datetime.now(datetime.timezone.utc)
        return_string = "INSERT INTO {0} VALUES ('{1}', '{2}', '{3}');".format(
            entry['table'], t.strftime("%Y-%m-%d %H:%M:%S"), spl_cmd, spl_resp)    
        print(return_string)
        cur = con.execute(return_string)
        con.commit()
    time.sleep(config["interval"])
modem.close()
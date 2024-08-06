#!/usr/bin/env python3

'''
Michael Kricheldorf

This code heavily copies the functions found in the `atinout.c` program
written by Håkon Løvdal (hlovdal@users.sourceforge.net)
https://atinout.sourceforge.net/

TODO: split each cmd into its own table
TODO: add cmd line support for changing device port, e.g. /dev/ttyUSB0
'''

import serial
import time
import datetime
import os
import sqlite3

script_path = os.getcwd()

cmd_list = ['AT', 'AT+CIND?', 'AT+VZWRSRP?', 'AT+VZWRSRQ?']
database_filename = script_path + "/modem_log.db"
table_name = "modem"

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

# setup modem serial comm
modem = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=False, rtscts=False, dsrdtr=False)

# connect to SQL database
con = sqlite3.connect(database_filename)
cur = con.cursor()

# create table if it doesn't already exist
cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{0}';".format(table_name))
if (cur.fetchone()[0] == 0):
    cur = con.execute("CREATE TABLE {0}(DATETIME text, COMMAND text, RESPONSE text);".format(table_name))

for cmd in cmd_list:
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
        table_name, t.strftime("%Y-%m-%d %H:%M:%S"), spl_cmd, spl_resp)    
    print(return_string)
    cur = con.execute(return_string)
    con.commit()
    
modem.close()
sys.exit()
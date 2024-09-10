#!/usr/bin/env python3

'''
TODO: figure out IP issues coming back strangely
'''

'''imports'''
import sqlite3
import socket
import datetime
import time
import os

'''setup'''

ip_format = [10, 10, 101]

# script path and config init
script_path = os.path.abspath(os.path.dirname(__file__))
config = {}

# connect to SQL database
db_path = "/var/log/network_metrics/rnode_log.db"
table_name = 'rssi'
try:
    con = sqlite3.connect(db_path, check_same_thread=False)
except:
    print("Could not find " + db_path + ". Exiting program.")
    sys.exit(1)
cur = con.cursor()

# create table if it doesn't already exist
cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{0}';".format(table_name))
if (cur.fetchone()[0] == 0):
        cur = con.execute("CREATE TABLE {0}(DATETIME TEXT, FROM_ADDR TEXT, TO_ADDR TEXT, RSSI TEXT);".format(table_name))

print("Database set up.")

'''main loop'''
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    print("Socket created.")
    svaddr = ('127.0.0.1', 50002)
    s.bind(svaddr)
    print(f"Server listening on {svaddr}")
    try:
        while True:
            is_to_addr = False
            # variables submitted to the database
            from_addr = "" # address of transmitter
            to_addr = ""   # address of receiver 
            rssi = -1

            data, addr = s.recvfrom(1024)
            # collect current datetime 
            t = datetime.datetime.now(datetime.timezone.utc)
            for i in range(len(data)):
                # gather RSSI hex
                if data[i] == 0x23 and data[i-1] == 0xc0:
                    rssi = data[i+1]

                # gather IP within domain, e.g. `10.10.101.#`
                if not(is_to_addr) and (len(data)-1 - i > 2) and (data[i] == ip_format[0]) and (data[i+1] == ip_format[1]) and (data[i+2] == ip_format[2]):
                    is_to_addr = True
                    from_addr = "{0}.{1}.{2}.{3}".format(data[i], data[i+1], data[i+2], data[i+3])
                    to_addr = "{0}.{1}.{2}.{3}".format(data[i+4], data[i+5], data[i+6], data[i+7])
                
            # submit data to sqlite database
            return_string = "INSERT INTO {0} VALUES ('{1}', '{2}', '{3}', '{4}')".format(
                table_name, t.strftime("%Y-%m-%d %H:%M:%S"), from_addr, to_addr, rssi)
            print(return_string)   
            cur = con.execute(return_string)
            con.commit()
    finally:
        s.close()
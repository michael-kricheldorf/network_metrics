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
script_path = '/home/ubuntu/miscellaneous/network_metrics'
config = {}

# connect to SQL database
database_file = '/home/ubuntu/miscellaneous/network_metrics/rnode_log.db'
table_name = 'rssi'
con = sqlite3.connect(database_file)
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
            #print(f"msg FROM {addr}: \n{data.decode()}")
            # collect current datetime 
            t = datetime.datetime.now(datetime.timezone.utc)
            for i in range(len(data)):
                # gather RSSI hex
                if data[i] == 0x23 and data[i-1] == 0xc0:
                    #print("{2} b: {0}\td: {1}".format(hex(data[i+1]), data[i+1], i))
                    rssi = data[i+1]

                # gather IP within domain, e.g. `10.10.101.#`
                if not(is_to_addr) and (len(data)-1 - i > 2) and (data[i] == ip_format[0]) and (data[i+1] == ip_format[1]) and (data[i+2] == ip_format[2]):
                    #print("{0} ip: {1}.{2}.{3}.{4}".format(i, data[i], data[i+1], data[i+2], data[i+3]))
                    is_to_addr = True
                    from_addr = "{0}.{1}.{2}.{3}".format(data[i], data[i+1], data[i+2], data[i+3])
                    to_addr = "{0}.{1}.{2}.{3}".format(data[i+4], data[i+5], data[i+6], data[i+7])
                
            # submit data to sqlite database
            return_string = "INSERT INTO {0} VALUES ('{1}', '{2}', '{3}', '{4}')".format(
                table_name, t.strftime("%Y-%m-%d %H:%M:%S"), from_addr, to_addr, rssi)
            print(return_string)   
            cur = con.execute(return_string)
            con.commit()
            #print(from_addr + " " + to_addr + " rssi: " + str(rssi))
    finally:
        s.close()
# # setup socket file
# socket_file = '/home/ubuntu/tncattach/serial_echo'
# try:
#     os.remove(socket_file)  # Remove any existing socket file
# except OSError:
#     pass

# # connect to SQL database
# database_file = '/home/ubuntu/miscellaneous/network_metrics/rnode_log.db'
# table_name = 'rssi'
# con = sqlite3.connect(database_file)
# cur = con.cursor()

# # create table if it doesn't already exist
# cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{0}';".format(table_name))
# if (cur.fetchone()[0] == 0):
#         cur = con.execute("CREATE TABLE {0}(DATETIME TEXT, FROM_ADDR TEXT, TO_ADDR TEXT, RSSI TEXT);".format(table_name))

# print("Database set up.")

# '''main loop'''
# with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as s:
#     print("Socket created.")
#     s.bind(socket_file)
#     print(f"Server listening on {socket_file}")
#     while True:
#         is_to_addr = False
#         # variables submitted to the database
#         from_addr = "" # address of transmitter
#         to_addr = ""   # address of receiver 
#         rssi = -1

#         data, addr = s.recvfrom(1024)
#         # collect current datetime 
#         t = datetime.datetime.now(datetime.timezone.utc)
#         for i in range(len(data)):
#             # gather RSSI hex
#             if data[i] == 0x23 and data[i-1] == 0xc0:
#                 #print("{2} b: {0}\td: {1}".format(hex(data[i+1]), data[i+1], i))
#                 rssi = data[i+1]

#             # gather IP within domain, e.g. `10.10.101.#`
#             if not(is_to_addr) and (len(data)-1 - i > 2) and (data[i] == ip_format[0]) and (data[i+1] == ip_format[1]) and (data[i+2] == ip_format[2]):
#                 #print("{0} ip: {1}.{2}.{3}.{4}".format(i, data[i], data[i+1], data[i+2], data[i+3]))
#                 is_to_addr = True
#                 from_addr = "{0}.{1}.{2}.{3}".format(data[i], data[i+1], data[i+2], data[i+3])
#                 to_addr = "{0}.{1}.{2}.{3}".format(data[i+4], data[i+5], data[i+6], data[i+7])
            
#         # submit data to sqlite database
#         return_string = "INSERT INTO {0} VALUES ('{1}', '{2}', '{3}', '{4}')".format(
#             table_name, t.strftime("%Y-%m-%d %H:%M:%S"), from_addr, to_addr, rssi)
#         print(return_string)   
#         cur = con.execute(return_string)
#         con.commit()
#         #print(from_addr + " " + to_addr + " rssi: " + str(rssi))
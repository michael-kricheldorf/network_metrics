#!/usr/bin/env python3
'''
TODO: clean up
TODO: make exit function
'''


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

'''classes'''
'''
this child class of Thread allows the thread function to return
a value upon being joined

code used from https://stackoverflow.com/a/65447493
'''
class ThreadThatReturnsValue(threading.Thread):
    def run(self):
        try:
            if self._target is not None:
                self.result = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs

'''functions'''
'''
this function reads the `/proc/net/dev` file until 
it receives an event signal from its host ping thread 

params:
    read_ev event object to block and loop for
    n       the interface to look for in /proc/net/dev
'''
def read_rx(read_ev, n):
    prev_val = 0
    val = 0
    while (read_ev.is_set()):
        dev_out = open("/proc/net/dev", mode='r').readlines()
        for line in dev_out[2:]:
            if n in line:
                # store second-most-recent byte value
                t = val
                val = float(line[line.index(":")+1:].split()[0])
                if val > t:
                    prev_val = t
    return prev_val

'''
thread function to ping and read from `/proc/net/dev` continuously

params:
    db      sql database connection
    lock    thread lock
    a       host alias
    n       interface
    addr    IP address
    pl      size of payload (bytes)
    to      timeout (sec)
    i       interval (sec)

 returns:
    0 when exited successfully, -1 and error message otherwise
'''
def ping(db, lock, a, n, addr, pl, to, i):
    # event to wake up rx-reading thread
    read_ev = threading.Event()
    while True:
        post_rx = None
        byte_diff = -1
        # get pre-TX no. bytes from `/proc/net/dev`
        dev_out = open("/proc/net/dev", mode='r').readlines()
        for line in dev_out[2:]:
            if n in line:
                byte_diff = float(line[line.index(":")+1:].split()[8])
        # ping 
        dt = datetime.datetime.now(datetime.timezone.utc)
        res = subprocess.Popen(["ping", addr, "-c 1", "-I" + n, "-s" + str(pl),"-W" + str(to)], stdout=subprocess.PIPE)
        # get post-TX no. bytes from `/proc/net/dev`
        dev_out = open("/proc/net/dev", mode='r').readlines()
        for line in dev_out[2:]:
            if n in line:
                byte_diff = float(line[line.index(":")+1:].split()[8]) - byte_diff
        # event to awaken sleepy thread until ping read completes
        read_ev.set()
        # create new thread
        read_thread = ThreadThatReturnsValue(target=read_rx, args=(read_ev, n))
        read_thread.start()
        res_str = res.stdout.read().decode('utf-8')
        read_ev.clear()
        read_thread.join()
        pre_rx = read_thread.result
        # get post-RX no. bytes from `/proc/net/dev`
        dev_out = open("/proc/net/dev", mode='r').readlines()
        for line in dev_out[2:]:
            if n in line:
                post_rx = float(line[line.index(":")+1:].split()[0])

        print(byte_diff, "+ (", post_rx, "-", pre_rx)
        byte_diff = byte_diff + (post_rx - pre_rx)

        try:
            l_ms = float(re.search(r"time=(\d+\.*\d*) ms", res_str).group(1))
        
        except AttributeError:
            l_ms = -1
            byte_diff = -1

        # generate return string
        return_string = "INSERT INTO {0} VALUES ('{1}', '{2}', '{3}', '{4}', {5}, {6}, {7}, {8}, {9});".format(
                        table_name, dt.strftime("%Y-%m-%d %H:%M:%S"), a, n, addr, i, pl, to, l_ms, byte_diff)
        #print(post_rx)
        print(return_string)

        # lock on database and add new row
        lock.acquire()
        db.execute(return_string)
        db.commit()
        lock.release()

        time.sleep(i)

    kill_read_ev.set()
    read_thread.join()
    return

'''init'''
# initialize paths
script_path = os.path.abspath(os.path.dirname(__file__))
config_path = script_path + "/ping_config.json"
db_name = "/ping_log.db"
db_path = script_path + db_name
table_name = "latency"

db_lock = threading.Lock()

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
    con = sqlite3.connect(db_path, check_same_thread=False)
except:
    print("Could not find " + db_path + ". Creating '" + db_name + "' in this directory.")
    f = open(db_name, "x")
    f.close()
    con = sqlite3.connect(db_name, check_same_thread=False)
cur = con.cursor()

# create table if it doesn't already exist
cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{0}';".format(table_name))
if (cur.fetchone()[0] == 0):
    cur = con.execute("CREATE TABLE {0}(DATETIME TEXT, ALIAS TEXT, INTERFACE TEXT, ADDRESS TEXT, INTERVAL_S INT, PL_SIZE INT, TIMEOUT_S INT, LATENCY_MS REAL, BYTES REAL);".format(table_name))

live_threads = []

for entry in config['addresses']:
    # get properties of each ping destination
    alias = entry['alias']
    interface = entry['interface']
    address = entry['address']
    pl_size = entry['pl_size']
    timeout = entry["timeout"]
    interval = entry["interval"]

    # create and call thread functions here
    t = threading.Thread(target=ping, args=(con, db_lock, alias, interface, address, pl_size, timeout, interval))
    live_threads.append(t)
    t.start()

for t in live_threads:
    t.join()

print("Threads joined, program done executing.")
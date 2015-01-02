import sqlite3
import trollius as asyncio
import time
#from datetime import datetime
from IPython import embed

import tellcore.telldus as td
#import tellcore.constants as const

class Service(object):
    def __init__(self):
        self.dbpath = "/home/pi/sensordb.sql"
        self.conn = None
        self.cur = None
        self._tablecache = []

    def connect_db(self):
        print("Connecting to db")
        self.conn = sqlite3.connect(self.dbpath)
        self.cur = self.conn.cursor()

    def check_or_create_table(self, tablename):
        if tablename in self._tablecache:
            return
        res = self.cur.execute("select * from sqlite_master where name='%s'" % tablename).fetchall()
        if not res:
            print("creating table")
            self.cur.execute("create table '%s' (timestamp STRING, value REAL)"%tablename)
        self._tablecache.append(tablename)
    
    def disconnect_db(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def loop(self):
        loop = asyncio.get_event_loop()
        dispatcher = td.AsyncioCallbackDispatcher(loop)
        core = td.TelldusCore(callback_dispatcher=dispatcher)
        core.register_sensor_event(self.sensor_event)
        print("Starting loop")
        loop.run_forever()

    def sensor_event(self, protocol, model, id_, dataType, value, timestamp, cid):
        string = "[SENSOR] {0} [{1}/{2}] ({3}) @ {4} <- {5}".format(id_, protocol, model, dataType, timestamp, value)
        print(string)
        if dataType == 1:
            tablename = str(id_) + "temperature"
        elif dataType == 2:
            tablename = str(id_) + "humidity"
        self.check_or_create_table(tablename)
        #tid = datetime.now().isoformat()
        tid = time.time()
        cmd = "insert into '%s' values (%s, %s)" % (tablename, tid, float(value))
        print cmd
        self.cur.execute(cmd)
        self.conn.commit()



if __name__ == "__main__":
    ser = Service()
    try:
        ser.connect_db()
        ser.loop()
    finally:
        ser.disconnect_db()

		


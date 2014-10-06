import sqlite3
import trollius as asyncio
from datetime import datetime
from IPython import embed

import tellcore.telldus as td
import tellcore.constants as const

class Service(object):
    def __init__(self):
        self.dbpath = "/home/pi/sensordb.sql"
        self.tablename = "sensors"
        self.conn = None
        self.cur = None

    def connect_db(self):
        print("Connecting to db")
        self.conn = sqlite3.connect(self.dbpath)
        self.cur = self.conn.cursor()
        res = self.cur.execute("select * from sqlite_master where name='%s'" % self.tablename).fetchall()
        if not res:
            print("creating table")
            self.cur.execute("create table '%s' (sensor int, datetime STRING, type INT, value REAL)"%self.tablename)
    
    def disconnect_db(self):
        if self.conn:
            self.conn.commit();
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
        if (10 < id_ < 30):
            tid = datetime.now().isoformat()
            cmd = "insert into '%s' values (%s, '%s', %s, %s)" % (self.tablename, id_, tid, dataType, float(value))
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

		


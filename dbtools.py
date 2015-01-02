import datetime 
import dateutil.parser

from IPython import embed
import sqlite3

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


class Tools(object):
    def __init__(self):
        self.dbpath = "sensordb.sql"
        self.conn = None 
        self.cur = None

    def connect_db(self):
        print("Connecting to db")
        self.conn = sqlite3.connect(self.dbpath)
        self.cur = self.conn.cursor()

    def check_or_create_table(self, tablename):
        res = self.cur.execute("select * from sqlite_master where name='%s'" % tablename).fetchall()
        if not res:
            print("creating table")
            self.cur.execute("create table '%s' (timestamp STRING, value REAL)"%tablename)
  
    def get_table_list(self):
        tables = []
        for res in self.cur.execute("select name from sqlite_master"):
            tables.append(res[0])
        return tables

    def get_count(self, tablename):
        cmd = "SELECT COUNT(*) FROM '{}'".format(tablename)
        return self.cur.execute(cmd).fetchone()[0]

    def get_all_tables_count(self):
        for name in self.get_table_list():
            try:
                print(name, ": ", self.get_count(name))
            except:
                print("Error reading table: ", name)

    def remove_noise_tables(self, nb=5):
        for name in self.get_table_list():
            try:
                count = self.get_count(name)
                if count < nb: 
                    cmd = "DROP TABLE '{}'".format(name)
                    print(cmd)
                    self.cur.execute(cmd)
                else:
                    print("keeping table: ", name)
            except:
                print("Error reading table: ", name)

    def show_tail(self, tablename):
        for res in self.cur.execute("select * from '{}' ORDER BY rowid ASC LIMIT 10".format(tablename)):
            print(res)

    def show_head(self, tablename):
        for res in self.cur.execute("select * from '{}' ORDER BY rowid DESC LIMIT 10".format(tablename)):
            print(res)



    def clean_table(self, tablename):
        self.check_or_create_table(tablename + "_week")
        self.check_or_create_table(tablename + "_all")
        start = self.cur.execute("select min(datetime(timestamp)) from '{table}'".format(table=tablename)).fetchone()[0]
        start = dateutil.parser.parse(start)
        period = datetime.timedelta(minutes=10)
        stop = datetime.datetime.now() - datetime.timedelta(minutes=10)

        starttime = start
        stoptime = start + period
        cmd = "select avg(datetime(timestamp)) from '{table} where timestamp < {starttime} and timestamp {stoptime}'".format(table=tablename, starttime=starttime.isoformat(), stoptime=stoptime.isoformat())

        return cmd 

    def convert_all_to_epoch(self):
        for tablename in self.get_table_list():
            self.convert_to_epoch(tablename)

    def convert_to_epoch(self, tablename):
        print("Converting ", tablename)
        cmd = "select rowid, timestamp from '{}'".format(tablename)
        for rowid, ts in self.cur.execute(cmd).fetchall():
            if type(ts) is float:
                print("ts is float", ts)
                continue
            try:
                ts = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
            except:
                ts = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")

            ts = unix_time(ts)
            cmd = "UPDATE '{}' SET timestamp={} WHERE rowid={}".format(tablename, ts, rowid)
            self.cur.execute(cmd)
        

     
    def disconnect_db(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

if __name__ == "__main__":
    t = Tools()
    try:
        t.connect_db()
        table = t.get_table_list()[0]
        embed()
    finally:
        t.disconnect_db()

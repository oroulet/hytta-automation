import sqlite3
import datetime
import statistics
import dateutil.parser

class Reduce(object):
    def __init__(self, dbpath):
        self.db = sqlite3.connect(dbpath)

    def check_or_create_table(self, tablename):
        res = self.db.execute("select * from sqlite_master where name='%s'" % tablename).fetchall()
        if not res:
            print("creating table: ", tablename)
            self.db.execute("create table '%s' (timestamp STRING, value REAL)"%tablename)
    
    def compress_data(self, sensorid):
        temp_table_name = sensorid + "temperature"
        hum_table_name = sensorid + "humidity"
        self.compress_table(temp_table_name)
        self.compress_table(hum_table_name)

    def compress_table(self, tablename):
        result = self.db.execute("SELECT rowid FROM '{}'".format(tablename))
        #if result.count() < 100:
            #print("table {} is probably just noise, removing".format(tablename))
            #return

        history_table = tablename + "_hours"
        self.check_or_create_table(history_table)
        result = self.db.execute("SELECT timestamp FROM '{}' ORDER BY rowid ASC LIMIT 1".format(tablename))
        ts = result.fetchone()[0]
        print ("oldest timestamp is : ", ts)
        oldest = dateutil.parser.parse(ts)
        oldest = datetime.datetime(year=oldest.year, month=oldest.month, day=oldest.day, hour=oldest.hour) #rounding to hour

        now = datetime.datetime.now() 
        end = now - datetime.timedelta(days=3)
        start = oldest
        while start < end:
            result = self.db.execute("SELECT rowid, * FROM '{}' WHERE datetime(timestamp) >= datetime('{}') AND datetime(timestamp) < datetime('{}')".format(tablename, start, start + datetime.timedelta(hours=1)))
            temps = []
            rowids = []
            for rowid, ts, temp in result:
                temps.append(temp)
                rowids.append(rowid)
            if len(temps) < 10:
                print("not ennough data for ", start, " ignoring")
                start += datetime.timedelta(hours=1)
                continue
            print("mean is: ", start, statistics.mean(temps))
            start += datetime.timedelta(hours=1)

if __name__ == "__main__":
    c = Reduce("sensordb.sql")
    c.compress_table("13temperature")

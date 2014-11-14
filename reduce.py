import sqlite3
import datetime
import time
#import statistics
#import dateutil.parser


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

    def get_oldest_timestamp(self, tablename):
        result = self.db.execute("SELECT timestamp FROM '{}' ORDER BY rowid ASC LIMIT 1".format(tablename))
        ts = result.fetchone()[0]
        print ("oldest timestamp is : ", ts)
        #oldest = dateutil.parser.parse(ts)
        #oldest = ISO8601ToDateTime(ts)
        oldest = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
        return datetime.datetime(year=oldest.year, month=oldest.month, day=oldest.day, hour=oldest.hour) #rounding to hour


    def compress_table(self, tablename):
        #result = self.db.execute("SELECT rowid FROM '{}'".format(tablename))
        #if result.count() < 100:
            #print("table {} is probably just noise, removing".format(tablename))
            #return

        history_table = tablename + "_hours"
        self.check_or_create_table(history_table)

        oldest = self.get_oldest_timestamp(tablename)

        now = datetime.datetime.now() 
        end = now - datetime.timedelta(hours=2)
        start = oldest
        while start < end:
            rowids = self.mean_and_save(tablename, history_table, start, start + datetime.timedelta(hours=1))
            self.remove_rows(tablename, rowids)
            start += datetime.timedelta(hours=1)

    def mean_and_save(self, origintable, savetable, startts, endts):
        result = self.db.execute("SELECT rowid, * FROM '{}' WHERE datetime(timestamp) >= datetime('{}') AND datetime(timestamp) < datetime('{}')".format(origintable, startts, endts))
        temps = []
        rowids = []
        for rowid, ts, temp in result:
            temps.append(temp)
            rowids.append(rowid)
        if len(temps) < 10:
            print("not ennough data for ", startts, " ignoring")
        else:
            mean = float(sum(temps))/len(temps)
            print("saving: ", savetable, startts, mean)
        return rowids

    def remove_rows(self, tablename, rowids):
        print("Removing ")#, rowids, " in ", tablename)


if __name__ == "__main__":
    c = Reduce("sensordb.sql")
    c.compress_table("13temperature")

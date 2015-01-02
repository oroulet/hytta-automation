import sqlite3
import datetime
import time
from IPython import embed
#import statistics
#import dateutil.parser

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def median(mylist):
    sorts = sorted(mylist)
    length = len(sorts)
    if not length % 2:
        return (sorts[length / 2] + sorts[length / 2 - 1]) / 2.0
    return sorts[length / 2]

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
        print ("oldest timestamp in: ", tablename, " is : ", ts)
        #oldest = dateutil.parser.parse(ts)
        #oldest = ISO8601ToDateTime(ts)
        oldest = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
        return datetime.datetime(year=oldest.year, month=oldest.month, day=oldest.day, hour=oldest.hour) #rounding to hour
        #oldest -= datetime.timedelta(minutes=oldest.minute%10, seconds=oldest.second, microseconds=oldest.microsecond) # rundt to 10 minutes
        #return oldest

    def get_newest_timestamp(self, tablename):
        try:
            result = self.db.execute("SELECT timestamp FROM '{}' ORDER BY rowid DESC LIMIT 1".format(tablename))
            ts = result.fetchone()[0]
            oldest = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            oldest = datetime.datetime.fromtimestamp(0)

        print ("newest timestamp in: ", tablename , " is : ", oldest)
        #oldest = dateutil.parser.parse(ts)
        #oldest = ISO8601ToDateTime(ts)
        return datetime.datetime(year=oldest.year, month=oldest.month, day=oldest.day, hour=oldest.hour) #rounding to hour
        #oldest -= datetime.timedelta(minutes=oldest.minute%10, seconds=oldest.second, microseconds=oldest.microsecond) # rundt to 10 minutes
        #return oldest

    def compress_table(self, tablename):
        history_table = tablename + "_hours"
        self.check_or_create_table(history_table)

        newest = self.get_newest_timestamp(history_table)

        oldest = self.get_oldest_timestamp(tablename)

        now = datetime.datetime.now() 
        #now -= datetime.timedelta(minutes=now.minute%10, seconds=now.second, microseconds=now.microsecond) # rundt to 10 minutes
        now -= datetime.timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # rundt to hour
        delete_end = now - datetime.timedelta(hours=48)
        end = now
        start = oldest
        while start < end:
            if start < newest:
                rowids = self.mean_and_save(tablename, history_table, start, start+datetime.timedelta(hours=1))
                if start <= delete_end:
                    self.remove_rows(tablename, rowids)
            start += datetime.timedelta(hours=1)

    def mean_and_save(self, origintable, savetable, startts, endts):
        cmd = "SELECT rowid, * FROM '{}' WHERE datetime(timestamp) >= datetime('{}') AND datetime(timestamp) < datetime('{}')".format(origintable, startts, endts)
        print(cmd)
        result = self.db.execute(cmd)
        vals = []
        rowids = []
        for rowid, ts, val in result:
            vals.append(val)
            rowids.append(rowid)
        print("Raw values are: ", vals)
        mean = median(vals)
        newvals = []
        for v in vals:
            if abs(v-mean) < 20:
                newvals.append(v)
        print("Filtered values are: ", newvals)
        vals = newvals
        mean = float(sum(vals))/len(vals)
        cmd = "INSERT INTO '{}' values ({}, {})".format(savetable, unix_time(startts), mean)
        print(cmd)
        return rowids

    def remove_rows(self, tablename, rowids):
        for rowid in rowids:
            cmd = "DELETE from '{}' WHERE rowid = {}".format(tablename, rowid)
            print(cmd)


if __name__ == "__main__":
    c = Reduce("sensordb.sql")
    embed()
    #c.compress_table("13temperature")

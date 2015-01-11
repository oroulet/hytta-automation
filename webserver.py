import json
import os
import datetime

from IPython import embed
import sqlite3
import cherrypy


import config #local configuration

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


class WebApp(object):
    @cherrypy.expose
    def index(self):
        return open('www/overview.html')

    @cherrypy.expose
    def plot(self, sensorid=11):
        return open('www/plot.html')

class DBQueryWebService(object):
    exposed = True

    def __init__(self, dbpath):
        self.dbpath = dbpath

    def GET(self, method, **kwargs):
        """
        dispatch request to local method
        """
        print(self.__dict__)
        return getattr(self, method)(**kwargs)

    def _get_last_data(self, sensorid, tablename):
        with sqlite3.connect(self.dbpath) as con:
            #cmd = "SELECT * FROM '{table}' ORDER BY datetime(timestamp) DESC LIMIT 1;".format(table=tablename)
            cmd = "SELECT * FROM '{table}' ORDER BY rowid DESC LIMIT 1;".format(table=tablename)
            result = con.execute(cmd)
            result = result.fetchall()
            for res in result:
                d = {}
                d["sensorid"] = sensorid 
                ts = res[0]
                ts = datetime.datetime.fromtimestamp(ts).isoformat()
                d["timestamp"] = ts 
                d["value"] = res[1]
            return json.dumps(d)

    def getLastTemperature(self, sensorid):
        """
        return only last  temperatur record for given sensor
        """
        tablename = str(sensorid) + "temperature"
        return self._get_last_data(sensorid, tablename)


    def getLastHumidity(self, sensorid):
        """
        return only last  temperatur record for given sensor
        """
        tablename = str(sensorid) + "humidity"
        return self._get_last_data(sensorid, tablename)

    def getTemperature(self, sensorid):
        """
        """
        start = datetime.datetime.now() - datetime.timedelta(hours=config.default_chart_period)
        start = unix_time(start)
        tablename = str(sensorid) + "temperature"
        #with sqlite3.connect(self.dbpath) as con:
            #cmd = "SELECT timestamp FROM '{table}' ORDER BY rowid DESC LIMIT 1;".format(table=tablename)
            #result = con.execute(cmd)
            #ts = result.fetchone()
        #stop = datetime.datetime.fromtimestamp(ts)
        #start = stop -
        return self._get_data(sensorid, tablename, start)

    def _get_data_json(self, sensorid, tablename, start):
        with sqlite3.connect(self.dbpath) as con:
            cmd = "SELECT * FROM '{}' WHERE timestamp > {};".format(tablename, start)
            d = {}
            d["sensorid"] = sensorid 
            data = {}
            d["data"] = data 
            result = con.execute(cmd)
            for res in result.fetchall():
                ts = res[0]
                ts = datetime.datetime.fromtimestamp(ts).isoformat()
                val = res[1]
                data[ts] = val
            return json.dumps(d)

    def _get_data(self, sensorid, tablename, start):
        with sqlite3.connect(self.dbpath) as con:
            cmd = "SELECT * FROM '{}' WHERE timestamp > {};".format(tablename, start)
            timestamps = []
            vals = []
            result = con.execute(cmd)
            for res in result.fetchall():
                ts = res[0]
                if type(ts) in (str, unicode):
                    continue
                ts = datetime.datetime.fromtimestamp(ts).isoformat()
                timestamps.append(ts)
                vals.append(res[1])
            d = {}
            d["timestamps"] = timestamps[::config.data_slicing]
            d["values"] = vals[::config.data_slicing]
            return json.dumps(d)



if __name__ == '__main__':
    conf = {
            'global': {
            'server.socket_port': config.port,
            'server.socket_host': config.host
                },
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.join(os.path.abspath(os.getcwd()), "www")
        },
        '/dbquery': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './css'
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './js'
        }

    }

    webapp = WebApp()
    webapp.dbquery = DBQueryWebService(config.db_path)
    cherrypy.quickstart(webapp, '/', conf)


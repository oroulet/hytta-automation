import json
import os
import datetime

from IPython import embed
import sqlite3
import cherrypy

class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return open('www/overview.html')


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

    #@cherrypy.tools.accept(media='text/plain')
    def getLastTemperature(self, sensorid):
        """
        return only last  temperatur record for given sensor
        """
        with sqlite3.connect(self.dbpath) as con:
            tablename = str(sensorid) + "temperature"
            cmd = "SELECT * FROM '{table}' ORDER BY date(datetime) DESC LIMIT 1;".format(table=tablename)
            result = con.execute(cmd)
            result = result.fetchall()
            for res in result:
                d = {}
                d["sensorid"] = sensorid 
                d["timestamp"] = res[0]
                d["value"] = res[1]
            return json.dumps(d)

    def getTemperature(self, startdatetime, enddatetime=None):
        if not enddatetime:
            enddatetime = datetime.datetime.now()
        #cmd = "SELECT * FROM '%s' WHERE date(datetime)>='%s';" % (self.tablename, startdatetime)

if __name__ == '__main__':
    conf = {
            'global': {
            'server.socket_port': 8080,
            'server.socket_host': '0.0.0.0'
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
        }
    }

    webapp = StringGenerator()
    webapp.dbquery = DBQueryWebService("/home/pi/sensordb.sql")
    cherrypy.quickstart(webapp, '/', conf)


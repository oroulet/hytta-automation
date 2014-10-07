import json
import os
import datetime

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

    #@cherrypy.tools.accept(media='text/plain')
    def GET(self, sensorid, datatype, startdatetime=None):
        """
        return only last record in db, otherwise from datetime 
        """
        with sqlite3.connect(self.dbpath) as con:
            tablename = str(sensorid) + datatype
            if not startdatetime:
                #cmd = "SELECT * FROM '{table}' WHERE sensor={sensor} AND type={datatype} AND datetime=(SELECT MAX(date(datetime)) FROM '{table}') LILMIT 1;".format(table=self.tablename, sensor=sensorid, datatype=datatype)
                cmd = "SELECT * FROM '{table}' ORDER BY column DESC LIMIT 1;".format(table=tablename)
            else:
                #FIXME: should limie amound of data, create min osv ...
                cmd = "SELECT * FROM '%s' WHERE date(datetime)>='%s';" % (tablename, startdatetime)
            result = con.execute(cmd)
            result = result.fetchall()
            listresult = []
            for res in result:
                d = {}
                d["sensor"] = res[0]
                d["timestamp"] = res[1]
                d["type"] = res[2]
                d["value"] = res[3]
                listresult.append(d) 
            return json.dumps(listresult)


if __name__ == '__main__':
    conf = {
            'global': {
            'server.socket_port': 8080,
            'server.socket_hosy': 'localhost'
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
    webapp.dbquery = DBQueryWebService("/tmp/test.sql")
    cherrypy.quickstart(webapp, '/', conf)


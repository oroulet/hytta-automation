#!/bin/sh
#

### BEGIN INIT INFO
# Provides:          hytta-web 
# Required-Start:    $network $remote_fs $syslog
# Required-Stop:     $network $remote_fs $syslog
# Should-Start:
# Should-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: collect data from sensors System
# Description:       This daemon will start cherrypy 
### END INIT INFO



set -x
workdir=/home/pi/hytta-automation/
 
start() {
    cd $workdir
    /usr/bin/python /home/pi/hytta-automation/webserver.py &
    echo "Server started."
}
 
stop() {
    pid=`ps -ef | grep '[p]ython /home/pi/hytta-automation/webserver.py' | awk '{ print $2 }'`
    echo $pid
    kill $pid
    sleep 2
    echo "Server killed."
}
 
case "$1" in
  start)
    start
    ;;
  stop)
    stop   
    ;;
  restart)
    stop
    start
    ;;
  *)
    echo "Usage: /etc/init.d/tornado-tts {start|stop|restart}"
    exit 1
esac
exit 0

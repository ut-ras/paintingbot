import conf
import os

from hardware.motor.server import *
from hardware.motor.modules.com import test_connection
## Initialize motors, testing

def main():
	pid = os.fork()
	if pid == 0:
		    os.system("celery -A hardware.motor.server.celery worker --concurrency=1")
	else:
		if conf.ROBOT_IP != '0.0.0.0':
			test_connection(conf.ROBOT_IP)

		app.run(host='0.0.0.0', port=conf.PORT)

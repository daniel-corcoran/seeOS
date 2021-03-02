# Here we make OS calls to power off, or restart, the device.
import os
import sys
import psutil
import logging
from tools.buzzer import disable_buzzer
import threading
import os
from app import app
import time
from tools.kiwilog import kiwi
log = kiwi.instance("tools.power")
# FIXME: This is not secure. We don't want users to have sudo access.

@app.route("/localAPI/power/off", methods=['POST', 'GET'])
def power_off():
    log.add_log("Power off command received")

    def power_off_command():
        time.sleep(1)
        log.add_log("[* superuser *] invoking /bin/bash shutdown -h now")
        os.system('echo %s|sudo -S %s' % ('mendel', 'shutdown -h now'))

    thread = threading.Thread(target=power_off_command, args=())
    thread.start()


@app.route("/localAPI/power/reboot", methods=['POST', 'GET'])
def reboot():
    log.add_log("Power off command received")
    def power_off_command():
        time.sleep(1)

        log.add_log("[* superuser *] invoking /bin/bash reboot -h now")
        os.system('echo %s|sudo -S %s' % ('mendel', ' reboot -h now'))

    thread = threading.Thread(target=power_off_command, args=())
    thread.start()


def restart_client():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """

    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        logging.error(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)
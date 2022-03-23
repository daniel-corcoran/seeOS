from subprocess import Popen, PIPE
from modules.kiwilog import kiwi
log = kiwi.instance('modules.temp')
from app import app
import json

@app.route('/measure_temp', methods=['POST', 'GET'])
def get_temp():

    command = 'cat /sys/class/thermal/thermal_zone0/temp'
    output = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = output.communicate()
    return str(int(int(stdout) / 1000 )) + '°C'
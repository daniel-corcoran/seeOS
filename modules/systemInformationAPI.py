import math
import psutil
from app import app
from flask import jsonify

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])


@app.route("/cpu_load", methods=['POST', 'GET'])
def cpu_load():
    # Return CPU load statistics via json
    pct = psutil.cpu_percent(percpu=True)
    d = {'a': pct[0], 'b': pct[1], 'c': pct[2], 'd': pct[3]}
    return jsonify(d)


@app.route("/memory", methods=['POST', 'GET'])
def memory():
    # Return memory
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    d = {'mem_total': convert_size(mem.total),
         'mem_used':  convert_size(mem.used),
         'mem_free': convert_size(mem.free),
         'swap_total': convert_size(swap.total),
         'swap_used': convert_size(swap.used),
         'swap_free': convert_size(swap.free)}
    return jsonify(d)


@app.route("/disk_capacity", methods=['POST', 'GET'])
def disk_capacity():
    # AJAX call to know how much space is remaining on the SD card.
    try:

        hdd = psutil.disk_usage('/home/mendel/sdcard')

        return jsonify({'total':convert_size(int(hdd.total)),
                        'used': convert_size(int(hdd.used)),
                        'free': convert_size(int(hdd.free))})
    except:
        hdd = psutil.disk_usage('/')

        return jsonify({'total': convert_size(int(hdd.total)),
                        'used': convert_size(int(hdd.used)),
                        'free': convert_size(int(hdd.free))})
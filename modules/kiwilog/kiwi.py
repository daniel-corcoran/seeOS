from datetime import datetime

log = {}
exc = {}
debug = {}

class instance:
    identifier = 'No identifier'
    def __init__(self, src, ):
        self.src = src

    def add_log(self, msg):
        global log
        global exc
    #!print('[INFO]\t' + self.src + '\t' +  msg + '\t' + str(datetime.now()))
        if self.src not in log:
            log[self.src] = {str(datetime.now()): msg}
        else:
            log[self.src][str(datetime.now())] = msg

    def add_exception(self, msg):
        print('\033[93m[ERR]\033[0m\t' + self.src + '\t' + msg + '\t' + str(datetime.now()))
        global log
        global exc
        if self.src not in exc:
            exc[self.src] = {str(datetime.now()): msg}
        else:
            exc[self.src][str(datetime.now())] = msg

    def add_debug(self, msg):
        print('[DEBUG]\t' + self.src + '\t' + msg + '\t' + str(datetime.now()))
        global log
        global exc
        if self.src not in exc:
            exc[self.src] = {str(datetime.now()): msg}
        else:
            exc[self.src][str(datetime.now())] = msg

    def get_logs(self):
        global log
        return log

    def get_exceptions(self):
        global exc
        return exc

    def get_debug(self):
        global debug
        return debug




    def save(self):
        print("FIXME")



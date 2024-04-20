import time
class Logger:

    @classmethod
    def log(self, src, msg):
        '''logs into the console'''
        print(time.strftime('[%d/%m/%Y - %H:%M:%S]') + ' ' + src + " :: " + msg) 
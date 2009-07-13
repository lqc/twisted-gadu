from twistedgadu import *

class GaduTest(object):
    def __init__(self):
        factory = GGClientFactory(self)
        reactor.connectTCP('91.197.13.83', 8074, factory)

    """Methods that should be overwritten by user"""
    def on_auth_got_seed(self, seed):
        print 'mamy seed: ', seed
        print 'hurej!'

    def on_authorised(self, null):
        print 'zalogowano!'
        print 'good!'
        

if __name__ == '__main__':
    GaduTest()
    reactor.run()
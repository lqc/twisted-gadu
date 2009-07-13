from twistedgadu import *

class GaduTest(object):

    """Methods that should be overwritten by user"""
    def on_auth_got_seed(self, seed):
        print 'mamy seed: ', seed
        print 'hurej!'

    def on_authorised(self, null):
        print 'zalogowano!'
        print 'good!'
        
def main():
    t = GaduTest()
    factory = GGClientFactory(t)
    reactor.connectTCP('91.197.13.83', 8074, factory)
    #factory.sendMessage()
    #factory.Login(4634020, 'xxxxxx', GGStatuses.Avail, 'test')
    reactor.run()
        

if __name__ == '__main__':
    main()

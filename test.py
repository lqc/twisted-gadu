from twistedgadu import *

class GaduTest(object):
    def on_auth_got_seed(self, conn, seed):
        print 'mamy seed: ', seed
        conn.login(seed)

    def on_login_ok(self, conn):
        print 'zalogowano!'

    def on_login_failed(self, conn):
        print 'logowanie nie powiodlo sie!'

    def on_need_email(self, conn):
        print 'musisz uzupelnic email!'

    def on_disconnecting(self, conn):
        print 'rozlaczanie!'
        
def main():
    t = GaduTest()
    factory = GGClientFactory(t)
    reactor.connectTCP('91.197.13.83', 8074, factory)
    #factory.sendMessage()
    #factory.Login(4634020, 'xxxxxx', GGStatuses.Avail, 'test')
    reactor.run()
        

if __name__ == '__main__':
    main()

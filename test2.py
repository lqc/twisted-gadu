from twistedgadu import *

# Jest to przykladowa aplikacja wykorzystujaca biblioteke twisted-gadu. Nie robi nic specjalnego - po prostu
# zmienia status z dostepnego na zajety i na odwrot a w opisie ustawia licznik ile razy status zostal zmieniony
# niestety GG ma blokade nawet wobec tego i po kilku takich zmianach blokuje nasz status...

class GaduTest(object):
    def __init__(self):
        factory = GGClientFactory(self)
        reactor.connectTCP('91.197.13.83', 8074, factory)

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

    def on_notify_reply(self, conn, contacts):
        ### To dopiero oznacza prawdziwe logowanie. Dopiero po tym evencie powinny byc wysylane pakiety uzytkownika do serwera
        # Moze sprawdzmy nasz status?
        print conn.get_actual_status()
        # i nasz opis
        print conn.get_actual_status_desc()
        conn.change_status(GGStatuses.AvailDescr, "test")
        desc = 0
        reactor.callLater(60, self.set_status_to_avail, conn, desc)

    def set_status_to_avail(self, conn, desc):
        desc = desc+1
        conn.change_status(GGStatuses.AvailDescr, str(desc))
        print "zmiana statusus na dostepny"
        reactor.callLater(60, self.set_status_to_busy, conn, desc)

    def set_status_to_busy(self, conn, desc):
        desc = desc+1
        conn.change_status(GGStatuses.BusyDescr, str(desc))
        print "zmiana statusus na zajety"
        reactor.callLater(60, self.set_status_to_avail, conn, desc)

if __name__ == '__main__':
    GaduTest()
    reactor.run()
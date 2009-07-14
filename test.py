from twistedgadu import *

# pokazuje na czym polegaja zdarzenia (eventy), opisuje je z krotsza
# pamietajmy ze na dzien dzisiejszy wszystkie te eventy musza byc zdefiniowane w kodzie

class GaduTest(object):
    def __init__(self):
        # tworzymy instancje klasy. Cos trzeba tlumaczyc? ;)
        # UWAGA! Ponizsza zmienna jest wymagana!
        self.contacts_list = ContactsList([Contact({'uin':3993939,'shown_name':'Tralala'}), Contact({'uin':4668758,'shown_name':'Anna'}), Contact({'uin':5120225,'shown_name':'kkszysiu'})])

    def on_auth_got_seed(self, conn, seed):
        # te zdarzenie jest wykonywane jesli uda nam sie pobrac seed potrzebny do zalogowania
        print 'mamy seed: ', seed
        #login zawsze owinien byc wykonywany w on_auth_got_seed
        #login przyjmuje seed, uin, password, status i opis
        conn.login(seed, 4634020, 'xxxxxx', GGStatuses.Avail, '')

    def on_login_ok(self, conn):
        #ten event informuje nas ze zostalismy poprawnie zalgoowani. Nie jest to jeszcze koniec
        # bowiem aby moc wysylac komendy i miec info o uzytkownikach musimy jeszcze odpytac serwer o info o kontaktach z listy
        print 'zalogowano!'

    def on_login_failed(self, conn):
        # ten event wystepuje jesli logowanie sie nie powiedzie. zazwyczaj oznacza to bledny seed lub nieprawidlowa nazwe uzytkonika i/lub haslo
        print 'logowanie nie powiodlo sie!'

    def on_need_email(self, conn):
        # event informuje o potrzebuie podania adresu email. Nie jest on juz chyba uzywany niemniej GG jeszcze go obsluguje...
        print 'musisz uzupelnic email!'

    def on_disconnecting(self, conn):
        # trzeba cos tlumaczyc? Event wystepuje gdy GG ozlaczy nas z serwerem. Najczesciej oznacza to ze podlaczyl sie nny klient uzywajacy naszego numeru GG
        print 'rozlaczanie!'

    def on_notify_reply(self, conn, contacts):
        # hurej! Jesli klient powiadomil nas o tym evencie oznacza to ze pobralismy ingo o kontaktach z naszej listy i jestesmuy gotowi do wysylania pakietow do serwera GG
        print 'info o kontaktach pobrane'
        #powinno wyswietlic moj opis
        print contacts[5120225].description
    
def main():
    t = GaduTest()
    factory = GGClientFactory(t)
    reactor.connectTCP('91.197.13.83', 8074, factory)
    #factory.sendMessage()
    #factory.Login(4634020, 'xxxxxx', GGStatuses.Avail, 'test')
    reactor.run()
        

if __name__ == '__main__':
    main()

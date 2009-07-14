import user
__author__="lreqc"
__date__ ="$2009-07-14 01:54:14$"

from twistedgadu.protocol import GaduClient
from twistedgadu.models import UserProfile, Contact
from twisted.internet import reactor, protocol
from twisted.python import log
import sys

class GaduClientFactory(protocol.ClientFactory):

    def __init__(self, profile):
        self.profile = profile

    def buildProtocol(self, addr):
        return GaduClient(self.profile)

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
    #    protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    #    connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
    #    protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        reactor.stop()



if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

    user = UserProfile(4634020, 'xxxxxx')
    user.put_contact(Contact(uin = 202, shown_name = 'Blip'))
    user.put_contact(Contact(uin = 1849224, shown_name = 'Lukasz'))

    # create factory protocol and application
    factory = GaduClientFactory(user)

    # connect factory to this host and port
    reactor.connectTCP('91.197.13.83', 8074, factory)

    # run 
    reactor.run()
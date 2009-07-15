#!/bin/env python

__author__="lreqc"
__date__ ="$2009-07-14 01:54:14$"

import gtk
from gtk import glade

from twisted.internet import gtk2reactor
gtk2reactor.install()

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

class MainApp(object):

    def __init__(self):
        self.gladefile = "simple_client.glade"
        self.widgetTree = glade.XML(self.gladefile)


        self.mainWindow = self.widgetTree.get_widget("MainWindow")
        self.mainWindow.connect("destroy", self.onWindowClose)
        self.sendButton = self.widgetTree.get_widget("send_button")
        self.messageEntry = self.widgetTree.get_widget("message_entry")

        tv = self.widgetTree.get_widget("message_view")
        self.msgBuf = gtk.TextBuffer()
        tv.set_buffer(self.msgBuf)

        self.widgetTree.signal_autoconnect({
            'on_send_button_clicked': self.onMessageSent
        })
        
        self.mainWindow.show()
        

    def onMessageSent(self, widget, data=None):
        self.msgBuf.insert_at_cursor('Hello!\n')

    def onWindowClose(self, widget, data=None):
        reactor.stop()
        return True

if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

    user = UserProfile( 1849224, 'guantanamo')
    user.put_contact(Contact(uin = 202, shown_name = 'Blip'))
    user.put_contact(Contact(uin = 4634020, shown_name = 'Tester2'))

    # create factory protocol and application
    factory = GaduClientFactory(user)

    # connect factory to this host and port
    # reactor.connectTCP('91.197.13.83', 8074, factory)
    # run
    MainApp()
    reactor.run()
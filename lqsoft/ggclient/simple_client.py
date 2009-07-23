#!/usr/bin/env python
# -*- coding: utf-8

__author__="lreqc"
__date__ ="$2009-07-14 01:54:14$"

import gtk

from twisted.internet import gtk2reactor
gtk2reactor.install()

from lqsoft.pygadu.twisted_protocol import GaduClient
from lqsoft.pygadu.models import UserProfile, Contact

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

    def __init__(self, profile):
        self.profile = profile
        
        # connect some callbacks to the model
        self.profile.onLoginSuccess = self.loginSuccess
        self.profile.onLoginFailure = self.loginFailed
        self.profile.onContactStatusChange = self.updateContact
        self.profile.onMessageReceived = self.messageReceived

        self.factory = GaduClientFactory(profile)

        self.gtk_builder = gtk.Builder();
        self.gtk_builder.add_from_file("simple_client.glade")

        self.mainWindow = self.gtk_builder.get_object("RoosterWindow")
        self.mainWindow.connect("destroy", self.onExit)

        unconnected = self.gtk_builder.connect_signals({
            'on_menu_connect_activate': self.connectUser,
            'on_menu_quit_activate': self.onExit,
           # 'on_menu_about_activate': self.onAbout,
        })
        print unconnected
        
        # status bar
        #self.statusBar = self.widgetTree.get_widget("main_statusbar")
        
        # extract some widgets
        #self.loginDialog = self.widgetTree.get_widget("LoginDialog")
        #self.loginDialog_uin = self.widgetTree.get_widget("uin_entry")
        #self.loginDialog_pass = self.widgetTree.get_widget("password_entry")
 
        #self.sendButton = self.widgetTree.get_widget("send_button")
        #self.messageEntry = self.widgetTree.get_widget("message_entry")

        #tv = self.widgetTree.get_widget("message_view")
        #self.msgBuf = gtk.TextBuffer()
        #tv.set_buffer(self.msgBuf)
        
        self.mainWindow.show()        

    def onMessageSent(self, widget, data=None):
        self.msgBuf.insert_at_cursor('Hello!\n')

    def onExit(self, widget, data=None):
        reactor.stop()
        return True

    def connectUser(self, widget, *args):
        """This is called when user selects "connect" from the main menu"""
        statusBar = self.gtk_builder.get_object("status_bar")

        self.__status_ctx_id = statusBar.get_context_id("Login status")
        statusBar.push(self.__status_ctx_id, "Authenticating...")
        
        #quicklogin
        self.profile.uin = 2578178
        self.profile.password = 'qwerty'
        reactor.connectTCP('91.197.13.83', 8074, self.factory)

        #self.loginDialog.show()

    def loginDialogResponse(self, widget, response_id, *args):
        self.loginDialog.destroy()

        if response_id == 2:
            self.profile.uin = int(self.loginDialog_uin.get_text())
            self.profile.password = self.loginDialog_pass.get_text()

            statusBar = self.gtk_builder.get_object("status_bar")

            statusBar.pop(self.__status_ctx_id)
            statusBar.push(self.__status_ctx_id, "Connecting...")

            reactor.connectTCP('91.197.13.83', 8074, self.factory)
        else:
            return False

    def loginSuccess(self):
        statusBar = self.gtk_builder.get_object("status_bar")
        statusBar.pop(self.__status_ctx_id)
        statusBar.push(self.__status_ctx_id, "Login done.")

    def loginFailed(self):
        statusBar = self.gtk_builder.get_object("status_bar")
        
        statusBar.pop(self.__status_ctx_id)
        statusBar.push(self.__status_ctx_id, "Login done.")

    def updateContact(self, contact):
        print contact

    def messageReceived(self, msg):
        print "Msg %d %d [%r] [%r]" % (msg.content.offset_plain, msg.content.offset_attrs, msg.content.plain_message, msg.content.html_message)


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

    user = UserProfile()
    user.putContact(Contact.simple_make(user, 202, 'Blip'))
    user.putContact(Contact.simple_make(user, 1849224, 'Łukasz Rekucki'))

    app = MainApp(user)

    reactor.run()
# -*- coding: utf-8
__author__="lreqc"
__date__ ="$2009-07-14 05:51:00$"

from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twistedgadu.comm.packets import *
from twistedgadu.comm.gadu_base import GGPacketHeader, GGStruct_Notify

import twisted.python.log as tlog

class GaduClient(Protocol):
    
    def __init__(self, profile):
        self.user_profile = profile # the user connected to this client
        self.beforeAuth = Deferred()
        self.loginSuccess = Deferred()

    def connectionMade(self):
        self.__buffer = ''        
        self.__chdr = None
        # Nie trzeba tu nic robiæ, bo to server pierwszy wysy³a nam wiadomoœæ

    def __pop_data(self, n):
        data, self.__buffer = self.__buffer[:n], self.__buffer[n:]
        return data

    def dataReceived(self, data):
        self.__buffer += data

        while True:
            if self.__chdr is not None:
                # if we are inside of a message
                hdr = self.__chdr

                if len(self.__buffer) < hdr.msg_length:
                    # not yet
                    break

                try:
                    msg_class = inclass_for_typeid(hdr.msg_type)
                except KeyError, e:
                    self.__pop_data(hdr.msg_length)
                    self._log('Ommiting message with type %d.' % hdr.msg_type)
                else:
                    msg, _ = msg_class.unpack( self.__pop_data(hdr.msg_length) )
                    self._messageReceived(hdr, msg)
                finally:
                    self.__chdr = None                  
            else:
                # we're waiting for a header
                if len(self.__buffer) < HEADER_LENGTH:
                    # no header yet
                    break

                self.__chdr, _ = GGPacketHeader.unpack(self.__pop_data(HEADER_LENGTH))
                # continue normally

        # end of data loop
    
    def _sendPacket(self, msg):
        # wrap the packet with a transport header
        self.transport.write( msg.as_packet(typeid_for_outclass(msg.__class__)) )

    def _messageReceived(self, hdr, msg):
        """Called when a full GG message has been received"""
        _, suffix = msg.__class__.__name__.split('_', 1)
        self._log("Calling action: " + suffix)
        getattr(self, '_handle' + suffix, self._log)(msg)

    # handlers
    def _handleWelcome(self, msg):
        self._log("Welcome seed is: " + str(msg.seed))

        self.beforeAuth.callback( msg.seed )

        login_klass = outclass_for_name('Login80')
        login = login_klass(uin=self.user_profile.uin, \
            login_hash=self.user_profile.password_hash(msg.seed) )
        self._sendPacket(login)

    def _handleLoginOk80(self, msg):
        self._log('Login successful.')
        self.loginSuccess.callback(None)

    def _handleLoginFailed(self, msg):
        self._log('Failed to login.')
        self.loginSuccess.errback(None)

    def _handleStatus80(self, msg):       
        self.user_profile.update_contact(msg.contact.uin, msg.contact)
        
        
    def _handleNotifyReply80(self, msg):
        for struct in msg.contacts:
            self.user_profile.update_contact(struct.uin, struct)
        

    def _handleDisconnecting(self, msg):
         self.loseConnection()

    def sendAllContacts(self):
        contacts = self.user_profile.contacts.values()

        if len(contacts) == 0:
            self.sendPacket( outclass_for_name('EmptyList')() )
            return

        nl_class = outclass_for_name('NotifyLast')
        nf_class = outclass_for_name('NotifyFirst')

        while len(contacts) > 400:
            batch, contacts = constacts[:400], contacts[400:]
            self._sendPacket( nf_class(contacts= \
                [GGStruct_Notify(uin=c.uin) for c in batch]) )

        self._sendPacket( nl_class(contacts= \
                [GGStruct_Notify(uin=c.uin) for c in contacts]) )
        self._log("Sent all contacts.")

    #
    # High-level interface callbacks
    #

    def _log(self, obj):
        tlog.msg( str(obj) )
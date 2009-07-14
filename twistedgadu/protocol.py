# -*- coding: utf-8
__author__="lreqc"
__date__ ="$2009-07-14 05:51:00$"

from twisted.internet.protocol import Protocol
from twistedgadu.comm.packets import *

from twistedgadu.comm.gadu_base import GGPacketHeader

import twisted.python.log as tlog

class GaduClient(Protocol):
    
    def __init__(self, profile):
        self.user_profile = profile # the user connected to this client

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

                msg_class = inclass_for_typeid(hdr.msg_type)
                msg = msg_class.unpack( self.__pop_data(hdr.msg_length) )
                    
                # clear the header                    
                self.__chdr = None
                self.messageReceived(hdr, msg)                                    
            else:
                # we're waiting for a header
                if len(self.__buffer) < HEADER_LENGTH:
                    # no header yet
                    break

                self.__chdr = GGPacketHeader.unpack(self.__pop_data(HEADER_LENGTH))
                # continue normally

        # end of data loop

    def sendPacket(self, msg):
        # wrap the packet with a transport header
        self.transport.write( msg.as_packet(typeid_for_outclass(msg.__class__)) )

    def messageReceived(self, hdr, msg):
        """Called when a full GG message has been received"""
        _, suffix = msg.__class__.__name__.split('_', 1)
        self._log("Calling action: " + suffix)
        getattr(self, 'handle' + suffix, self._log)(msg)

    # handlers
    def handleWelcome(self, msg):
        self._log("Welcome seed is: " + str(msg.seed))

        login_klass = outclass_for_name('Login80')
        login = login_klass(uin=self.user_profile.uin, \
            login_hash=self.user_profile.password_hash(msg.seed) )
        self.sendPacket(login)

    def handleLoginOk80(self, msg):
        self._log('Login successful.')

    def handleLoginFailed(self, msg):
        self._log('Failed to login.')

#    def sendAllContacts(self):
#        values = self.user_profile.contacts.values
#        if len(values) == 0:
#            self.sendPacket( outclass_for_name('EmptyList')() )
#            return
#
#        while len(values) > 400:
            

        


    def _log(self, obj):
        tlog.msg( str(obj) )
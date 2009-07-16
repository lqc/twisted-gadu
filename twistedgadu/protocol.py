# -*- coding: utf-8
__author__="lreqc"
__date__ ="$2009-07-14 05:51:00$"

from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twistedgadu.comm.packets import *
from twistedgadu.comm.gadu_base import GGPacketHeader, GGStruct_Notify

import twisted.python.log as tlog
import struct

class GaduClient(Protocol):
    
    def __init__(self, profile):
        self.user_profile = profile # the user connected to this client
        self.doLogin = Deferred()
        self.doLogin.addCallbacks(profile._creditials, self._onInvalidCreditials)
        self.doLogin.addCallbacks(self._doLogin, self._onLoginFailed)
        self.doLogin.addErrback(self._onLoginFailed)

        self.loginSuccess = Deferred()
        self.loginSuccess.addCallbacks(self._sendAllContacts, self._onLoginFailed)
        self.loginSuccess.addCallbacks(profile._loginSuccess, self._onLoginFailed)
        self.loginSuccess.addErrback(self._onLoginFailed)

    def connectionMade(self):
        self.__buffer = ''        
        self.__chdr = None
        # Nie trzeba tu nic robi¿, bo to server pierwszy wysy¿a nam wiadomo¿¿

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
        self.__seed = msg.seed
        self.doLogin.callback(self.__seed)
        
    def _doLogin(self, result, *args, **kwargs):
        self._log("Sending creditials to the server.")
        login_klass = outclass_for_name('Login80')        
        result[1].update( struct.pack("<i", self.__seed) )
        login = login_klass(uin=result[0], login_hash=result[1].digest())
        self._sendPacket(login)
        return True

    def _onLoginFailed(self, failure, *args, **kwargs):
        print 'Login failed.'
        failure.printTraceback()
        self.user_profile.onLoginFailure()
        return failure

    def _onInvalidCreditials(self, failure, *args, **kwargs):
        print "User didn't provide necessary info"
        failure.printTraceback()
        self._onLoginFailed(failure, *args, **kawrgs)

    def _handleLoginOk80(self, msg):
        print 'Login almost done - send the notify list.'
        self.loginSuccess.callback(self)

    def _handleLoginFailed(self, msg):
        print 'Server sent - login failed'
        self.loginSuccess.errback(None)

    def _handleStatus80(self, msg):       
        self.user_profile._update_contact(msg)
        
    def _handleNotifyReply80(self, msg):
        for struct in msg.contacts:
            self.user_profile.update_contact(struct)

    def _handleDisconnecting(self, msg):
         self.loseConnection()

    def _sendAllContacts(self, result, *args, **kwargs):
        contacts = list( self.user_profile.itercontacts() )

        if len(contacts) == 0:
            self.sendPacket( outclass_for_name('EmptyList')() )
            return

        nl_class = outclass_for_name('NotifyLast')
        nf_class = outclass_for_name('NotifyFirst')

        while len(contacts) > 400:
            batch, contacts = constacts[:400], contacts[400:]
            self._sendPacket( nf_class(contacts= \
                [GGStruct_Notify(uin=uin) for (uin, _) in batch]) )

        self._sendPacket( nl_class(contacts= \
                [GGStruct_Notify(uin=uin) for (uin, _) in contacts]) )
        self._log("Sent all contacts.")
        return self

    #
    # High-level interface callbacks
    #

    def _log(self, obj):
        tlog.msg( str(obj) )

# -*- coding: utf-8
__author__="lreqc"
__date__ ="$2009-07-14 05:51:00$"

from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
import twisted.python.log as tlog

from lqsoft.pygadu.network import *
from lqsoft.pygadu.packets import Resolver

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
        # Nie trzeba tu nic robi�, bo to server pierwszy wysy�a nam wiadomo��

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
                    msg_class = Resolver.by_IDi(hdr.msg_type)
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
                if len(self.__buffer) < PACKET_HEADER_LENGTH:
                    # no header yet
                    break

                self.__chdr, _ = GaduPacketHeader.unpack(\
                    self.__pop_data(PACKET_HEADER_LENGTH))
                # continue normally

        # end of data loop
    
    def _sendPacket(self, msg):
        # wrap the packet with a transport header
        self.transport.write( msg.as_packet() )

    def _messageReceived(self, hdr, msg):
        """Called when a full GG message has been received"""        
        self._log("Calling action: " + msg.__class__.__name__)
        getattr(self, '_handle' + msg.__class__.__name__, self._log)(msg)

    # handlers
    def _handleWelcomePacket(self, msg):
        self._log("Welcome seed is: " + str(msg.seed))
        self.__seed = msg.seed
        self.doLogin.callback(self.__seed)
        
    def _doLogin(self, result, *args, **kwargs):
        self._log("Sending creditials to the server.")
        login_klass = Resolver.by_name('LoginPacket')
        result[1].update( struct.pack("<i", self.__seed) )
        login = login_klass(uin=result[0], login_hash=result[1].digest())
        self._sendPacket(login)
        return True

    def _onLoginFailed(self, failure, *args, **kwargs):
        print 'Login failed.'
        failure.printTraceback()
        self.user_profile.onLoginFailure(failure)
        return failure

    def _onInvalidCreditials(self, failure, *args, **kwargs):
        print "User didn't provide necessary info"
        failure.printTraceback()
        self._onLoginFailed(failure, *args, **kawrgs)

    def _handleLoginOKPacket(self, msg):
        print 'Login almost done - send the notify list.'
        self.loginSuccess.callback(self)

    def _handleLoginFailedPacket(self, msg):
        print 'Server sent - login failed'
        self.loginSuccess.errback(None)

    def _handleStatusUpdatePacket(self, msg):
        self.user_profile._updateContact(msg.contact)
        
    def _handleStatusNoticiesPacket(self, msg):
        for struct in msg.contacts:
            self.user_profile._updateContact(struct)

    def _handleMessageInPacket(self, msg):
        self.user_profile.onMessageReceived(msg)

    def _handleDisconnectPacket(self, msg):
         self.loseConnection()

    def _sendAllContacts(self, result, *args, **kwargs):
        contacts = list( self.user_profile.itercontacts() )

        if len(contacts) == 0:
            self._sendPacket( Resolver.by_name('NoNoticePacket')() )
            return self

        nl_class = Resolver.by_name('NoticeLastPacket')
        nf_class = Resolver.by_name('NoticeFirstPacket')

        while len(contacts) > 400:
            batch, contacts = constacts[:400], contacts[400:]
            self._sendPacket( nf_class(contacts= \
                [StructNotice(uin=uin) for (uin, _) in batch]) )

        self._sendPacket( nl_class(contacts= \
                [StructNotice(uin=uin) for (uin, _) in contacts]) )
        self._log("Sent all contacts.")
        return self

    #
    # High-level interface callbacks
    #

    def _log(self, obj):
        tlog.msg( str(obj) )

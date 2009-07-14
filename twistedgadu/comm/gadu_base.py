# -*- coding: utf-8
__author__="lreqc"
__date__ ="$2009-07-14 01:07:32$"

from twistedgadu.util.cstruct import *
from twistedgadu.util import Enum

class GGPacketHeader(CStruct):
    """Struktura opisuj¹ca nag³ówek pakietu w GG"""
    msg_type        = IntField(0, True)
    msg_length      = IntField(1, True)

    def __str__(self):
        return '[GGHDR: type=%d, length %d]' % (self.msg_type, self.msg_length)

class GGMsg(CStruct):    
    """Wspólna nadklasa dla wszystkich wiadomoœci w GG"""
    def as_packet(self, type):
        data = self.pack()
        hdr = GGPacketHeader(msg_type=type, msg_length=len(data))
        return hdr.pack() + data

#
# Wiadomoœci przychodz¹ce
#
class GGMsg_Welcome(GGMsg):
    seed = IntField(0)
    
class GGMsg_SendMsgAck(GGMsg):
    MSG_STATUS = Enum({
        'BLOCKED': 0x0001, 'DELIVERED': 0x0002,
        'QUEUED': 0x0003, 'MBOXFULL': 0x0004,
        'NOT_DELIVERED': 0x0006
    })

    msg_status  = IntField(0)
    recipient   = IntField(1)
    seq         = IntField(2)

class GGMsg_LoginFailed(GGMsg):
    pass

class GGMsg_Disconnecting(GGMsg):
    pass

class GGMsg_DisconnectAck(GGMsg):
    pass

class GGMsg_Notify(GGMsg):
    TYPE = Enum({
        'BUDDY':    0x01,
        'FRIEND':   0x02,
        'BLOCKED':  0x04
    })
    uin             = IntField(0)
    type            = ByteField(1)

class GGMsg_NotifyFirst(GGMsg_Notify):
    pass

class GGMsg_NotifyLast(GGMsg_Notify):
    pass

class GGMsg_NeedEmail(GGMsg):
    pass
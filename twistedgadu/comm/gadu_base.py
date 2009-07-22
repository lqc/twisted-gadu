# -*- coding: utf-8
__author__="lreqc"
__date__ ="$2009-07-14 01:07:32$"

from lqsoft.cstruct.common import CStruct
from lqsoft.cstruct.fields import complex, numeric, text

from twistedgadu.util import Enum

class GGPacketHeader(CStruct):
    """Struktura opisująca nagłówek pakietu w GG"""
    msg_type        = numeric.UIntField(0)
    msg_length      = numeric.UIntField(1)

    def __str__(self):
        return '[GGHDR: type=%d, length %d]' % (self.msg_type, self.msg_length)

class GGMsg(CStruct):    
    """Wspólna nadklasa dla wszystkich wiadomości w GG"""
    def as_packet(self, type):
        data = self.pack()
        hdr = GGPacketHeader(msg_type=type, msg_length=len(data))
        return hdr.pack() + data

    def __str__(self):
        return self.__class__.__name__
#
# Wiadomości przychodzące
#
class GGMsg_Welcome(GGMsg):
    seed = numeric.IntField(0)
    
class GGMsg_SendMsgAck(GGMsg):
    MSG_STATUS = Enum({
        'BLOCKED': 0x0001, 'DELIVERED': 0x0002,
        'QUEUED': 0x0003, 'MBOXFULL': 0x0004,
        'NOT_DELIVERED': 0x0006
    })

    msg_status  = numeric.IntField(0)
    recipient   = numeric.IntField(1)
    seq         = numeric.IntField(2)

class GGMsg_LoginFailed(GGMsg):
    pass

class GGMsg_Disconnecting(GGMsg):
    pass

class GGMsg_DisconnectAck(GGMsg):
    pass


class GGStruct_Notify(CStruct):
    TYPE = Enum({
        'BUDDY':    0x01,
        'FRIEND':   0x02,
        'IGNORE':  0x04
    })
    
    uin             = numeric.UIntField(0)
    type            = numeric.UByteField(1, default=0x03)

    def __str__(self):
        return "%d[%d]" (self.uin, self.type)

class GGMsg_NotifyFirst(GGMsg):
    contacts        = complex.ArrayField(0, complex.StructField(0, struct=GGStruct_Notify), length=-1)

class GGMsg_NotifyLast(GGMsg):
    contacts        = complex.ArrayField(0, complex.StructField(0, struct=GGStruct_Notify), length=-1)

class GGMsg_AddNotify(GGMsg):
    contanct        = complex.StructField(0, struct=GGStruct_Notify)

class GGMsg_RemoveNotify(GGMsg):
    contanct        = complex.StructField(0, struct=GGStruct_Notify)

class GGMsg_Pong(GGMsg):
    pass

class GGMsg_ListEmpty(GGMsg):
    pass

# unused ?
class GGMsg_NeedEmail(GGMsg):
    pass

class GGMsg_Ping(GGMsg):
    pass

    

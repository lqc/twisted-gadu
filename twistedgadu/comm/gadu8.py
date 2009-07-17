# -*- coding: utf-8
#
__author__= "lreqc"
__date__ = "$2009-07-13 17:06:21$"
__doc__ = """Struktury danych pakietów przesyłanych przez Gadu-Gadu w wersji 8.0"""

from twistedgadu.util.cstruct import *
from twistedgadu.util import Enum

import twistedgadu.comm.gadu_base as gadu

import hashlib
import struct

# structures
class GGStruct_Status80(CStruct):
    uin             = IntField(0)
    status          = IntField(1)
    flags           = IntField(2)
    remote_ip       = IntField(3)
    remote_port     = ShortField(4)
    image_size      = ByteField(5)
    reserved01      = ByteField(6)
    reserved02      = IntField(7)
    description     = VarcharField(8)

# messages

class GGMsg_Login80(gadu.GGMsg):
    uin             = IntField(0, True, None)
    language        = StringField(1, 2, 'pl')
    hash_type       = ByteField(2, True, 0x02)
    login_hash      = StringField(3, 64)
    status          = IntField(4, True, 0x02)
    flags           = IntField(5, True, 0x03)
    features        = IntField(6, True, 0x37)
    local_ip        = IntField(7)
    local_port      = ShortField(8)
    external_ip     = IntField(9)
    external_port   = ShortField(10)
    image_size      = ByteField(11, True, 0xff)
    unknown01       = ByteField(12, True, 0x64)
    version         = VarcharField(13, "Gadu-Gadu Client build 8.0.0.9103")
    description     = VarcharField(14)

    def update_hash(self, password, seed):
        """Uaktualnij login_hash używając algorytmu SHA1"""
        hash = hashlib.new('sha1')
        hash.update(password)
        hash.update(struct.pack('<i', seed))
        self.login_hash = hash.digest()


class GGStruct_Conference(CStruct):
    attr_type       = ByteField(0)
    rcp_count       = IntField(1)
    recipients      = ArrayField(2, IntField, length='rcp_count')
    

class GGStruct_Message(CStruct):
    CLASS = Enum({
        'QUEUED':   0x0001,
        'MESSAGE':  0x0004,
        'CHAT':     0x0008,
        'CTCP':     0x0010,
        'NOACK':    0x0020,
    })

    klass               = IntField(0)
    offset_plain        = IntField(1) # tekst
    offset_attrs        = IntField(2) # atrybuty
    html_message        = NullStringField(3, end_bound='offset_plain')
    plain_message       = NullStringField(4, start_bound='offset_plain', end_bound='offset_attrs')
    # the problem here is that some structures are optional
    # and they all can occur :(
    attr_conference     = StructInline(5, GGStruct_Conference, prefix="\x01")
    attr_formating      = StructInline(6, prefix="\x02")




class GGMsg_RecvMsg80(gadu.GGMsg):
    sender              = IntField(0)
    seq                 = IntField(1)
    time                = IntField(2)
    content             = StructInline(3, GGStruct_Message)

class GGMsg_LoginOk80(gadu.GGMsg):
    reserved       = IntField(0, True)

# outgoinf messages
class GGMsg_SendMsg80(gadu.GGMsg):   
    recipient           = IntField(0)
    seq                 = IntField(1)
    content             = StructInline(2, GGStruct_Message)

class GGMsg_NewStatus80(gadu.GGMsg):
    STATUS = Enum({
        'NOT_AVAILBLE':         0x0001,
        'NOT_AVAILBLE_DESC':    0x0015,
        'FFC':                  0x0017,
        'FFC_DESC':             0x0018,
        'AVAILBLE':             0x0002,
        'AVAILBLE_DESC':        0x0004,
        'BUSY':                 0x0003,
        'BUSY_DESC':            0x0005,
        'DND':                  0x0021,
        'DND_DESC':             0x0022,
        'HIDDEN':               0x0014,
        'HIDDEN_DESC':          0x0016,
        'DND':                  0x0021,
        'BLOCKED':              0x0006,
        'MASK_FRIEND':          0x8000,        
        'MASK_GFX':             0x0100,
        'MASK_STATUS':          0x4000,
    })

    status          = IntField(0)
    flags           = IntField(1)
    description     = VarcharField(2)

class GGMsg_NotifyReply80(gadu.GGMsg):
    contacts        = StructArray(0, GGStruct_Status80)

class GGMsg_Status80(gadu.GGMsg):
    contact         = StructInline(0, GGStruct_Status80)    


# listy kontaktów
class GGMsg_UserListReq80(gadu.GGMsg):
    TYPE = Enum({
        'PUT':      0x00,
        'PUT_MORE': 0x01,
        'GET':      0x02,
    })

    type    =   ByteField(0)
    data    =   NullStringField(1)

class GGMsg_UserListReply80(gadu.GGMsg):
    TYPE = Enum({
        'PUT_REPLY':        0x00,
        'PUT_REPLY_MORE':   0x02,
        'GET_REPLY_MORE':   0x04,
        'GET_REPLY':        0x06,
    })

    type    =   ByteField(0)
    data    =   NullStringField(1)

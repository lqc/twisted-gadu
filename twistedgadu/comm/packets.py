# -*- coding: utf-8
__author__="lreqc"
__date__ ="$2009-07-14 01:04:28$"

from twistedgadu.comm.gadu8 import *
from twistedgadu.comm.gadu_base import *

from twistedgadu.util import reverse_dict

HEADER_LENGTH = 8

GG_Inbound, GG_InboundR = reverse_dict({
    0x0001: GGMsg_Welcome,
    0x0005: GGMsg_SendMsgAck,
    0x0009: GGMsg_LoginFailed,
    0x000b: GGMsg_Disconnecting,
    0x000d: GGMsg_DisconnectAck,
    #0x000e: gadu.GGMsg_PubDir50Reply,
    0x0014: GGMsg_NeedEmail,

    #0x001f: gadu_dcc.GGMsg_Dcc_Info,
    #0x0020: gadu_dcc.GGMsg_Dcc_New,
    #0x0021: gadu_dcc.GGMsg_Dcc_Accept,
    #0x0022: gadu_dcc.GGMsg_Dcc_Reject,
    #0x0023: gadu_dcc.GGMsg_Dcc_IdReply,
    #0x0025: gadu_dcc.GGMsg_Dcc_Aborted,

    #0x0027: gadu.GGMsg_XmlEvent,

    #0x002a: gadu8.GGMsg80Beta_Status,
    #0x002b: gadu8.GGMsg80Beta_NotifyReply,

    #0x002c: gadu.GGMsg_XmlAction,

    0x002e: GGMsg_RecvMsg80,
    #0x0030: gadu8.GGMsg80_UserListReply,
    0x0035: GGMsg_LoginOk80,
    #0x0036: gadu8.GGMsg80_Status,
    0x0037: GGMsg_NotifyReply80
})

GG_Outbound, GG_OutboundR = reverse_dict({
    0x0008: GGMsg_Pong,
    0x000d: GGMsg_AddNotify,
    0x000e: GGMsg_RemoveNotify,
    0x000f: GGMsg_NotifyFirst, # notifyFirst
    0x0010: GGMsg_NotifyLast, # notifyLast
    0x0012: GGMsg_ListEmpty,
    # 0x0014: gadu.GGMsg_PubDir50Request,

    #0x001f: gadu_dcc.GGMsg_Dcc_Info,
    #0x0020: gadu_dcc.GGMsg_Dcc_New,
    #0x0021: gadu_dcc.GGMsg_Dcc_Accept,
    #0x0022: gadu_dcc.GGMsg_Dcc_Reject,
    #0x0023: gadu_dcc.GGMsg_Dcc_IdReply,
    #0x0025: gadu_dcc.GGMsg_Dcc_Aborted,

    0x002d: GGMsg_SendMsg80,
    # 0x002f: gadu8.GGMsg_UserListRequest80,
    0x0031: GGMsg_Login80,
    0x0038: GGMsg_NewStatus80,
})

def inclass_for_typeid(id):
    return GG_Inbound[id]

def outclass_for_typeid(id):
    return GG_Outbound[id]

def outclass_for_name(string):
    return eval('GGMsg_' + string)

def typeid_for_outclass(cls):
    return GG_OutboundR[cls]

__all__ = ['inclass_for_typeid', 'outclass_for_typeid', \
    'outclass_for_name', 'typeid_for_outclass', 'HEADER_LENGTH']
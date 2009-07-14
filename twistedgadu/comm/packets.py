# -*- coding: utf-8
__author__="lreqc"
__date__ ="$2009-07-14 01:04:28$"

import twistedgadu.comm.gadu8 as gadu8
import twistedgadu.comm.gadu_base as gadu
from twistedgadu.util import Enum

GG_Inbound = Enum({
    0x0001: gadu.GGMsg_Welcome,
    0x0005: gadu.GGMsg_SendMsgAck,
    0x0009: gadu.GGMsg_LoginFailed,
    0x000b: gadu.GGMsg_Disconnecting,
    0x000d: gadu.GGMsg_DisconnectAck,
    #0x000e: gadu.GGMsg_PubDir50Reply,
    0x0014: gadu.GGMsg_NeedEmail,

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

    0x002e: gadu8.GGMsg80_RecvMsg,
    #0x0030: gadu8.GGMsg80_UserListReply,
    0x0035: gadu8.GGMsg80_LoginOk,
    #0x0036: gadu8.GGMsg80_Status,
    #0x0037: gadu8.GGMsg80_NotifyReply
})

GG_Outbound = Enum({
    0x0008: gadu.GGMsg_Pong,
    0x000d: gadu.GGMsg_AddNotify,
    0x000e: gadu.GGMsg_RemoveNotify,
    0x000f: gadu.GGMsg_NotifyFirst, # notifyFirst
    0x0010: gadu.GGMsg_NotifyLast, # notifyLast
    0x0012: gadu.GGMsg_ListEmpty,
    0x0014: gadu.GGMsg_PubDir50Request,

    #0x001f: gadu_dcc.GGMsg_Dcc_Info,
    #0x0020: gadu_dcc.GGMsg_Dcc_New,
    #0x0021: gadu_dcc.GGMsg_Dcc_Accept,
    #0x0022: gadu_dcc.GGMsg_Dcc_Reject,
    #0x0023: gadu_dcc.GGMsg_Dcc_IdReply,
    #0x0025: gadu_dcc.GGMsg_Dcc_Aborted,

    0x002d: gadu8.GGMsg80_SendMsg,
    0x002f: gadu8.GGMsg80_UserListRequest,
    0x0031: gadu8.GGMsg80_Login,
    0x0038: gadu8.GGMsg80_NewStatus,
})
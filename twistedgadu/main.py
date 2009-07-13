#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2009 Krzysztof 'kkszysiu' Klinikowski

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor, defer
from twisted.python import log
import sys
import struct

from IncomingPackets import *
from OutgoingPackets import *
from HeaderPacket import GGHeader
from Helpers import *
from GGConstans import *
from Exceptions import *
from Contacts import *

log.startLogging(sys.stdout)

gg_uin = 4634020
gg_passwd = 'xxxxxx'
gg_status = GGStatuses.Avail
gg_desc = 'test'
contacts_list = ContactsList([Contact({'uin':3993939,'shown_name':'Tralala'}), Contact({'uin':4668758,'shown_name':'Anna'})])
#contacts_list = ContactsList()

class GGClient(Protocol):
    def __init__(self):
        self.__uin = gg_uin
        print 'self.uin: ', self.__uin
        print 'gg_uin: ', gg_uin
        self.password = gg_passwd
        self.status = gg_status
        self.desc = gg_desc

        self.__contacts_list = contacts_list

        self._header = True
        self.__local_ip = "127.0.0.1"
        self.__local_port = 1550
        self.__external_ip = "127.0.0.1"
        self.__external_port = 0
        self.__image_size = 255
        self.seed = None

    def sendPacket(self, msg):
        print 'PacketSending'
        header = GGHeader()
	header.read(msg)
        print 'OUT header.type: ', header.type

        self.transport.write(msg)

    def connectionMade(self):
        Protocol.connectionMade(self)
	print 'connected'
        self._conn = self.factory._conn
        #self.sendPacket("Hello, world!")
        #self.sendPacket("What a fine day it is.")
        #self.sendPacket(self.end)

    def dataReceived(self, data):
        print 'received data: ', data
        header = GGHeader()
	header.read(data)
        print 'header.type: ', header.type
#        self.factory.clientReady(self)
	if header.type == GGIncomingPackets.GGWelcome:
            print 'packet: GGWelcome'
            in_packet = GGWelcome()
            in_packet.read(data, header.length)
            self.seed = in_packet.seed
            d = defer.Deferred()
            d.callback(self.seed)
            d.addCallback(self._conn.on_auth_got_seed)
            d = None
            self._login(self.seed)
        if header.type == GGIncomingPackets.GGLoginOK:
            print 'packet: GGLoginOK'
            d = defer.Deferred()
            d.callback(None)
            d.addCallback(self._conn.on_authorised)
            self._send_contacts_list()
            print 'wyslano liste kontaktow'
            self._ping()
        if header.type == GGIncomingPackets.GGUserListReply:
            print 'packet: GGUserListReply'
            d = defer.Deferred()
            d.callback(None)
            d.addCallback(self.on_userlistreply)

    def _login(self, seed):
        print '_login'
	out_packet = GGLogin(self.__uin, self.password, self.status, seed, self.desc, self.__local_ip, \
                            self.__local_port, self.__external_ip, self.__external_port, self.__image_size)
        self.sendPacket(out_packet.get())

    def _send_contacts_list(self):
        """
        Wysyla do serwera nasza liste kontaktow w celu otrzymania statusow.
        Powinno byc uzyte zaraz po zalogowaniu sie do serwera.
        UWAGA: To nie jest eksport listy kontaktow do serwera!
        """
        assert self.__contacts_list  == None or type(self.__contacts_list) == ContactsList
        print 'czas wyslac nasza liste kontaktow :D'
        if self.__contacts_list == None or len(self.__contacts_list) == 0:
            print 'yupp. wysylamy pusta liste kontaktow'
            out_packet = GGListEmpty()
            self.sendPacket(out_packet.get())
            return

        uin_type_list = [] # [(uin, type), (uin, type), ...]
        for contact in self.__contacts_list.data: #TODO: brrrrrrr, nie .data!!!!
            uin_type_list.append((contact.uin, contact.user_type))
        sub_lists = Helpers.split_list(uin_type_list, 400)

        for l in sub_lists[:-1]: #zostawiamy ostatnia podliste
            out_packet = GGNotifyFirst(l)
            self.sendPacket(out_packet.get())
        # zostala juz ostatnia lista do wyslania
        out_packet = GGNotifyLast(sub_lists[-1])
        self.sendPacket(out_packet.get())

    def _ping(self):
        """
        Metoda wysyla pakiet GGPing do serwera
        """
        out_packet = GGPing()
        self.sendPacket(out_packet.get())
        print "[PING]"
        reactor.callLater(10, self._ping)
        
    """Methods that should be overwritten by user"""


    def on_authorised(self, null):
        print 'zalogowano!'

    def on_userlistreply(self, null):
        print 'odebrano liste kontaktow!'

class GGClientFactory(ClientFactory):
    protocol = GGClient
    def __init__(self, conn):
        self._conn = conn

    def startedConnecting(self, connector):
	print 'connection started'

    def clientConnectionFailed(self, connector, reason):
        print 'connection failed:', reason.getErrorMessage()
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print 'connection lost:', reason.getErrorMessage()
        reactor.stop()

    def buildProtocol(self, addr):
      p = self.protocol()
      p.factory = self
      p.factory.instance = p
      return p


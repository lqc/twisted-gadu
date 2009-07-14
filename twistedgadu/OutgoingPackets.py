#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id: OutgoingPackets.py 65 2008-01-14 19:44:25Z ghandal $

import time
import types
import sys
import struct
from HeaderPacket import GGHeader
#from Networking import Connection
from GGConstans import *
import Helpers
from Helpers import Enum

GGOutgoingPackets = Enum({
	"GGNewStatus":0x0002, #Zmiana statusu
	"GGPing":0x0008, #Ping
	"GGSendMsg":0x000b, #Wyslanie wiadomosci
	"GGLogin":0x000c, #Logowanie sie przed GG 6.0
	"GGAddNotify":0x000d, #Dodanie do listy kontaktow
	"GGRemoveNotify":0x000e, #Usuniecie z listy kontaktow
	"GGNotifyFirst":0x000f, #Poczatkowy fragment listy kontaktow wiekszej niz 400 wpisow
	"GGNotifyLast":0x00010, #Ostatni fragment listy kontaktow
	"GGListEmpty":0x0012, #Nasza lista kontaktow jest pusta
	"GGLoginExt":0x0013, #Logowanie przed GG 6.0
	"GGPubDir50Request":0x0014, #Zapytanie katalogu publicznego
	"GGLogin60":0x0015, #Logowanie
	"GGUserListRequest":0x0016, #Zapytanie listy kontaktow na serwerze
	"GGLogin70":0x0019, #Logowanie
	"GGUserlistRequest":0x0016 #Wysylanie kontaktow do serwera Gadu-Gadu
	})

class GGOutgoingPacket(object):
	"""
	"Abstrakcyjna" klasa pakietow wysylanych do serwera
	"""
	def send(self):
		pass


class GGLogin(GGOutgoingPacket):
	"""
	Pakiet ten wysylamy do serwera, zeby sie zalogowac
	"""
	def __init__(self, uin, password, status, seed, description = "", local_ip = "127.0.0.1", local_port = 1550, \
				external_ip = "127.0.0.1", external_port = 0, image_size = 255, time = 0):
		"""
		uin - numer gadu-gadu (int)
		password - haslo (string)
		status - status poczatkowy (GGStatus)
		seed - seed z pakietu GGWelcome (int)
		"""
		assert type(uin) == types.IntType
		assert type(password) == types.StringType
		#assert type(status) in GGStatus
		#assert type(seed) == types.IntType or type(seed) == types.LongType
		assert type(description) == types.StringType and len(description) <= 70
		assert type(local_ip) == types.StringType
		assert type(local_port) == types.IntType
		assert type(external_ip) == types.StringType
		assert type(external_port) == types.IntType
		assert type(time) == types.IntType
		assert type(image_size) == types.IntType
		
		self.uin = uin
		self.password = password
		self.status = status
		self.seed = seed
		self.local_ip = local_ip
		self.local_port = local_port
		self.description = description
		self.external_ip = external_ip
		self.external_port = external_port
		self.image_size = image_size
		self.time = time
		self.version = 0x25 # GG 7.7

	def get(self):
		"""
		data = struct.pack("<IBIIIBIHIHBB%dsI" % (len(self.description) + 1),
		#data = struct.pack("<IB64sIIBIHIHBB%dsI" % (len(self.description) + 1),
			self.uin, 
			0x01, 
			Helpers.gg_login_hash(self.password, self.seed), 
			self.status, 
			self.version, 
			0x00, 
			Helpers.ip_to_int32(self.local_ip), 
			self.local_port, 
			Helpers.ip_to_int32(self.external_ip), 
			self.external_port, 
			self.image_size, 
			0xbe,
			self.description,
			self.time)

		connection.send(repr(GGHeader(GGOutgoingPackets.GGLogin, len(data))) + data)
		"""
		data = struct.pack("<IIIIBIhIhBB%dsI" % (len(self.description) + 1),
			self.uin, Helpers.gg_login_hash(self.password, self.seed), self.status, self.version, 0x00,
			Helpers.ip_to_int32(self.local_ip), self.local_port, Helpers.ip_to_int32(self.external_ip), self.external_port,
			self.image_size, 0xbe, self.description, self.time)
		return (repr(GGHeader(GGOutgoingPackets.GGLogin60, len(data))) + data)

class GGNewStatus(GGOutgoingPacket):
	"""
	Pakiet ten wysylamy do serwera, zeby zmienic status
	"""
	def __init__(self, status, description = '', time = None):
		"""
		status - status (GGStatus)
		description - opis statusu (string)
		time - czas w sekundach od 1.01.1970
		"""
		assert type(status) == types.IntType
		assert type(description) == types.StringType and len(description) <= 70
		#assert type(time) == types.IntType or type(time) == types.LongTime
		
		self.status = status
		self.description = description
		self.time = time

	def get(self):
		if self.status == GGStatuses.Avail or self.status == GGStatuses.NotAvail or self.status == GGStatuses.Busy or self.status == GGStatuses.Invisible or self.status == GGStatuses.Blocked:
			data = struct.pack("<I", self.status)
		else: # status z opisem
			if self.time == None: #bez czasu
				data = struct.pack("<I%ds" % (len(self.description),), self.status, self.description) 
			else:
				data = struct.pack("<I%dsBI" % (len(self.description), ), self.status, self.description, 0x00, self.time)
		return (repr(GGHeader(GGOutgoingPackets.GGNewStatus, len(data))) + data)
		
class GGSendMsg(GGOutgoingPacket):
	"""
	Pakiet wysylamy do serwera, zeby wyslac wiadomosc
	"""
	def __init__(self, rcpt, msg, seq = 0, msg_class = 0x0004):
		"""
		rcpt - numer odbiorcy
		seq - numer serwencyjny wiadomosci
		msg_class - klasa wiadomosci
		msg - wiadomosc
		"""
		assert type(rcpt) == types.IntType and rcpt > 0
		assert type(seq) == types.IntType
		assert type(msg_class) == types.IntType
		assert type(msg) == types.StringType and len(msg) <= 2000
		
		self.rcpt = rcpt
		self.seq = seq
		self.msg_class = msg_class
		self.msg = msg
		
	def send(self, connection):
		assert type(connection) == Connection
		
		data = struct.pack("<III%ds" % (len(self.msg) + 1), self.rcpt, self.seq, self.msg_class, self.msg)
		connection.send(repr(GGHeader(GGOutgoingPackets.GGSendMsg, len(data))) + data)
		
class GGPing(GGOutgoingPacket):
	"""
	Co jakis czas trzeba wysylac do serwera GG pakiet GGPing. W przeciwnym przypadku, serwer nas rozlaczy.
	"""
	def __init__(self):
		pass
	
	def get(self):
		return repr(GGHeader(GGOutgoingPackets.GGPing, 0))

class GGListEmpty(GGOutgoingPacket):
	"""
	Jesli nie mamy nikogo na liscie kontaktow, wysylamy ten pakiet - np. zaraz po zalogowaniu sie
	"""
	def __init__(self):
		pass
	
	def get(self):
            return repr(GGHeader(GGOutgoingPackets.GGListEmpty, 0))

class GGNotifyFirst(GGOutgoingPacket):
	"""
	Pierwsze wpisy (kazde po 400 kontaktow zawieraja) listy kontaktow, ktora wysylamy serwerowi po polaczeniu.
	"""
	def __init__(self, gg_notify_list):
		"""
		gg_notify_list list to lista krotek postaci: (uin, typ_uzytkownika)
		"""
		assert type(gg_notify_list) == types.ListType
		for notify in gg_notify_list:
			assert type(notify) == types.TupleType
			assert len(notify) == 2
			assert type(notify[0]) == types.IntType and type(notify([1])) in GGUserTypes
		assert len(gg_notify_list) == 400
		
		self.__gg_notify_list = gg_notify_list
	
	def get(self):
		data = ""
		for notify in self.__gg_notify_list:
			data += struct.pack("<IB", notify[0], notify[1])
		return (repr(GGHeader(GGOutgoingPackets.GGNotifyFirst, len(data))) + data)

class GGNotifyLast(GGOutgoingPacket):
	"""
	Ostatnie wpisy listy kontaktow (maksymalnie 400), ktore wysylamy zaraz po podlaczaniu. Jesli lista kontaktow
	zawiera <= 400 kontaktow to wysylamy jedynie ten pakiet. Jesli wiecej, to wysylamy najpierw pakiety GGNotifyFirst,
	a na koncu ten pakiet
	"""
	def __init__(self, gg_notify_list):
		"""
		gg_notify_list to lista krotek postaci: (uin, typ_uzytkownika)
		"""
		assert type(gg_notify_list) == types.ListType
		for notify in gg_notify_list:
			assert type(notify) == types.TupleType
			assert len(notify) == 2
			#assert type(notify[0]) == types.IntType and type(notify[1]) in GGUserTypes
		assert len(gg_notify_list) <= 400 #TODO: <= czy < ??? W protokole jest niejasno napisane... :(
		
		self.__gg_notify_list = gg_notify_list
	
	def get(self):
		data = ""
		for notify in self.__gg_notify_list:
			data += struct.pack("<IB", int(notify[0]), notify[1])
		return (repr(GGHeader(GGOutgoingPackets.GGNotifyLast, len(data))) + data)

class GGAddNotify(GGOutgoingPacket):
	"""
	Jesli w trakcie dzialania sesji chcemy kogos dodac do kontaktow, to wysylamy do serwera infomacje o nim.
	Po wyslaniu tego pakietu, serwer bezdie nas informowal o zmianach statusu tego kontaktu.
	"""
	def __init__(self, uin, user_type = 0x3):
		self.uin = uin
		self.user_type = user_type
	
	def send(self, connection):
		assert type(connection) == Connection
		data = struct.pack("<IB", self.uin, self.user_type & 0xff)
		connection.send(repr(GGHeader(GGOutgoingPackets.GGAddNotify, len(data))) + data)

class GGRemoveNotify(GGOutgoingPacket):
	"""
	Jesli w trakcie dzialania sesji chcemy kogos usunac z listy kontaktow, to wysylamy do serwera infomacje o nim.
	Po wyslaniu tego pakietu, serwer przestanie nas informowac o zmianach statusu tego kontaktu.
	Jesli podamy user_type (patrz protokol), to mozemy zmienic rodzaj uzytkowinka (niekoniecznie usuwajac go z serwerowej listy kontaktow).
	"""
	def __init__(self, uin, user_type = 0x0):
		self.uin = uin
		self.user_type = user_type
	
	def send(self, connection):
		assert type(connection) == Connection
		data = struct.pack("<IB", self.uin, self.user_type & 0xff)
		connection.send(repr(GGHeader(GGOutgoingPackets.GGRemoveNotify, len(data))) + data)
	


class GGPubDir50Request(GGOutgoingPacket):
	"""
	Pakiet sluzacy do odpytywania katalogu publicznego
	"""
	def __init__(self, request, reqtype = GGPubDirTypes.Search):
		assert type(request) == types.StringType or  type(request) == types.DictType
		
		if type(request) == types.StringType:
			self.request = request
		else:
			self.request = Helpers.dict_to_request(request)
		self.reqtype = reqtype
		self.seq = int(time.time())
		
	def send(self, connection):
		assert type(connection) == Connection
		
		data = struct.pack("<BI%ds" % (len(self.request) + 1), self.reqtype, self.seq, self.request)
		connection.send(repr(GGHeader(GGOutgoingPackets.GGPubDir50Request, len(data))) + data)
		
class GGUserListRequest(GGOutgoingPacket):
	"""
	Pakiet sluzacy do wysylania listy kontaktow na serwer Gadu-Gadu
	TODO: poprawa, bo to chyba nie dziala
	"""
	def __init__(self, reqtype, request):
		assert type(request) == types.StringType
		assert reqtype in GGUserListTypes
		
		self.reqtype = reqtype
		self.request = request
		
	def send(self, connection):
		assert type(connection) == Connection
		
		data = struct.pack("<B%ds" % (len(self.request) + 1), self.reqtype, self.request)
		connection.send(repr(GGHeader(GGOutgoingPackets.GGUserlistRequest, len(data))) + data)

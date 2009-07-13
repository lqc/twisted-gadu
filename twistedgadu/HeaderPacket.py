#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id: HeaderPacket.py 94 2008-01-17 00:23:38Z cinu $

import types
import struct

class GGHeader(object):
	"""
	Kazdy pakiet wysylany/pobierany do/od serwera zawiera na poczatku
	naglowek - tym naglowkiem jest wlasnie struktura GGHeader.
	"""
	def __init__(self, type_=0, length=0):
		assert type(type_) == types.IntType
		assert type(length) == types.IntType
		
		self.type = type_
		self.length = length

	def read(self, data):
		self.type, self.length = struct.unpack("<II", data[:8])
	
	def __repr__(self):
            return struct.pack("<II", self.type, self.length)

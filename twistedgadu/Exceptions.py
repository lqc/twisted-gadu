#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id: Exceptions.py 73 2008-01-15 19:00:25Z ghandal $

class GGException(Exception):
	"""
	Wyj "typu" gadu-gadu.
	"""
	pass

class GGUnexceptedPacket(GGException):
	"""
	Wyjatek gadu-gadu dla nieoczekiwanego pakietu.
	"""
	pass
	
class GGNotLogged(GGException):
	"""
	Wyjatek gadu-gadu - niezalogowany uzytkownik.
	"""
	pass

class GGServerNotOperating(GGException):
	"""
	Wyjatek gadu-gadu. Serwer nie odpowiada.
	"""
	pass
	
class GGBadTokenVal(GGException):
	"""
	Wyjatek gadu-gadu. Bledny token.
	"""
	pass

class GGNotInContactsList(GGException):
	"""
	Wyjatek gadu-gadu. Nie ma uzytkownika w liscie kontaktow.
	"""
	pass
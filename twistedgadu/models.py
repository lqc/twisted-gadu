# -*- coding: utf-8
__author__="lreqc"
__date__ ="$2009-07-14 07:33:27$"

import hashlib, struct

class UserProfile(object):
    def __init__(self, contacts={}):
        self.__hashelem = None
        self.contacts = contacts
        self.__connection = None
        
    def __set_password(self, value):
        self.__hashelem = hashlib.new('sha1')
        self.__hashelem.update(value)

    password = property(None, __set_password)

    def password_hash(self, seed):
        h = self.__hashelem.copy()
        h.update( struct.pack("<i", seed) )
        return h.digest()

    def get_contact(self, uin):
        return self.contacts[uin]

    def put_contact(self, contact):
        self.contacts[contact.uin] = contact

    def update_contact(self, uin, struct):
        self.contacts[uin].update_with_struct(struct)

    # high-level interface

    @property
    def connected(self):
        """Is the profile currently used in an active connection"""
        return self.__connection is not None

    # stuff that user can use
    def setNotifyState(self, uin, new_state):
        pass

    def sendTextMessage(self, text):
        pass

    def setMyState(self, new_state, new_description=''):
        pass

    def importContacts(self):
        pass

    def exportContacts(self):
        pass



    # stuff that should be implemented by user
    def onCreditialsNeeded(self):
        """This should return a 2-tuple containing the UIN and a raw password data"""
        return None

    def onLoginSuccess(self):
        """Called when login is completed."""
        pass

    def onLoginFailure(self):
        """Called after an unsuccessful login."""
        pass

    def onContantStatusChange(self, contact):
        """Called when a status of a contact has changed."""
        pass



            



class Contact(object):
    """
    Klasa reprezentujaca pojedynczy kontakt. Zawiera nastepujace pola (wszystkie publiczne):
        * uin - numer uzytkownika
        * name - imie uzytkownika
        * surname - nazwisko uzytkownika
        * shown_name - nazwa wyswietlana
        * nick - pseudonim uzytkownika
        * mobilephone - numer telefonu komorkowego
        * group - nazwa grupy
        * email - adres email uzytkownika
        * available - okresla dzwieki zwiazane z pojawieniem sie danej osoby i przyjmuje wartosci 0 (uzyte zostana ustawienia globalne),
            1 (dzwiek powiadomienia wylaczony) lub 2 (zostanie odtworzony plik okreslony w polu available_source)
        * available_source - sciezka do pliku opisanego wyzej
        * message - dziala podobnie do available, z tym, ze okresla dzwiek przychodzacej wiadomosci
        * message_source - sciezka do dzwieku odgrywanego przy otrzymaniu wiadomosci (opis powyzej)
        * hidden - okresla, czy bedziemy dostepni (0) czy niedostepni (1) dla danej osoby w trybie 'tylko dla znajomych'
        * telephone - numer telefonu
    Powyzsze pola mozemy przekazac w konstruktorze klase w formie slownika na dwa sposoby. Pierwszy z nich podaje slownik z kluczami
    o nazwach wlasciwosci (jedynym wymaganym kluczem jest 'uin') badz w formacie z slownika z kluczem 'request_string' o wartosci postaci:
    name;surname;nick;shown_name;mobilephone;group;uin;email;available;available_source;message;message_source;hidden;telephone
    Oprocz powyzszych pol, klasa posiada jeszcze pola modyfikowane przez klasy GGNotifyReply oraz GGStatus:
        * status - status uzytkownika
        * ip - adres IP uzytkownika do bezposrednich polaczen
        * port - port do bezposrednich polaczen
        * version - wersja klienta
        * image_size - maksymalny rozmiar przyjmowanej grafiki
        * description - opis (moze byc pusty)
        * return_time - data powrotu uzytkownika (jesli nie ma, to = 0)
        * user_type - typ uzytkownika (z klasy GGUserTypes)

    Przyklady uzycia:
        1. Contact({'uin':12345, 'name':'Tola', 'shown_name':'Tola', 'hidden':1, 'message':2, 'message_source':'/home/user/message.wav'})
        Utworzy kontakt o numerze 12345, nazwie 'Tola', wyswietlanej nazwie 'Tola', ukryty w trybie 'tylko dla znajomych' oraz ze zdefiniowanym
        dzwiekiem odgrywanym podczas przychodzacej wiadomosci

        2. Contact({'request_string':'Tola;;;Tola;;;12345;;0;;1;/home/user/message.wav;1;'})
        Utworzy kontakt jak wyzej.
    """
    # status = GGStatuses.NotAvail
    ip = 0
    port = 0
    version = 0 #zera sa po to, zeby sie nie odwolywac do None, jesli pola nie zostaly jeszcze wypelnione
    image_size = 0
    description = ""
    return_time = 0
    type = 0x03
    # user_type = GGUserTypes.Normal

    RQ_STRING_FORMAT = (\
        ('name', str),\
        ('surname', str),\
        ('nick', str),\
        ('shown_name', str),\
        ('mobilephone', str),\
        ('group', str),\
        ('uin', int),\
        ('email', str),\
        ('availble', int),\
        ('availble_source', str),\
        ('message', int),\
        ('message_source', str),\
        ('hidden', int),\
        ('telephone', str)\
    )

    def __init__(self, **kwargs):
        if not kwargs.has_key('uin'):
            raise ValueError("Kontakt musi mie� numer UIN.")

        self.uin = int(kwargs['uin'])
        self.name = kwargs.get('name', '')
        self.surname = kwargs.get('surname', '')
        self.nick = kwargs.get('nick', '')
        self.shown_name = kwargs.get('shown_name', '')
        self.mobilephone = kwargs.get('mobilephone', '')
        self.group = kwargs.get('group', '')
        self.email = kwargs.get('email', '')
        self.availble = kwargs.get('availble', 0)
        self.availble_source = kwargs.get('availble_source', '')
        self.message = kwargs.get('message', 0)
        self.message_source = kwargs.get('message_source', '')
        self.hidden = kwargs.get('hidden', 0)
        self.telephone = kwargs.get('telephone', '')

    def update_with_struct(self, struct):
        self.status = struct.status
        self.description = struct.description
        self._trigger_updated()

    def _trigger_updated(self):
        print "Contact %d updated to: %x %s" % (self.uin, self.status, self.description)

    @classmethod
    def from_request_string(cls, rqs):
        dict = {}
        for (fmt, value) in zip(cls.RQ_STRING_FORMAT, rqs.split(';')):
            dict[fmt[0]] = fmt[1](value)
        return cls(**dict)

    def request_string(self):
        return ";".join( [ str(self.__getattribute__(fmt[0])) for fmt in self.RQ_STRING_FORMAT] )
# -*- coding: utf-8
#(C) Marek Chrusciel, 
#    Jakub Kosinski, 
#    Marcin Krupowicz,
#    Mateusz Strycharski
#
# $Id: Contacts.py 94 2008-01-17 00:23:38Z cinu $


from GGConstans import *
from Exceptions import *
import types

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
    status = GGStatuses.NotAvail
    ip = 0
    port = 0
    version = 0 #zera sa po to, zeby sie nie odwolywac do None, jesli pola nie zostaly jeszcze wypelnione
    image_size = 0
    description = ""
    return_time = 0
    user_type = GGUserTypes.Normal

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
            raise ValueError("Kontakt musi mieæ numer UIN.")
            
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

    @classmethod
    def from_request_string(cls, rqs):
        dict = {}
        for (fmt, value) in zip(cls.RQ_STRING_FORMAT, rqs.split(';')):         
            dict[fmt[0]] = fmt[1](value)
        return cls(**dict)
        
    def request_string(self):
        return ";".join( [ str(self.__getattribute__(fmt[0])) for fmt in self.RQ_STRING_FORMAT] )

class ContactsList(list):
    """
    Klasa reprezentujaca liste kontaktow GG. Wpisy sa obiektami klast Contact. Konstruktor przyjmuje dwa rodzaje parametrow.
    Pierwszy z nich to lista obiektow typu Contact, drugi to zawartosc pliku z kontaktami (wartosci oddzielone srednikami, opis w klasie Contact)
    Dostep do kontaktow realizowany jest za pomoca uin, np. list['12345'] zwroci obiekt Contact o uin=12345 lub None w przypadku, gdy kontaktu
    nie ma na liscie.
    """
    def __init__(self, contacts = []):
        assert type(contacts) == types.ListType or types.StringType
        if type(contacts) == types.ListType:
            for c in contacts:
                assert type(c) == Contact
            self.data = contacts
        else:
            list = contacts.split("\n")
            tmp = []
            for c in list:
                if c != "" and c != "GG70ExportString,;":
                    tmp.append({'request_string':c})
            clist = []
            for c in tmp:
                clist.append(Contact(c))
            self.data = clist
    
    def add_contact(self, contact):
        """
        Metoda dodajaca kontakt. Jako parametr przyjmuje obiekt klasy Contact lub napis w formacie pliku kontaktow Gadu-Gadu.
        """
        if type(contact) == types.StringType:
            c = Contact(contact)
        elif type(contact) == Contact:
            c = contact
        else:
            raise AssertionError
        
        if self[c.uin] != None: #jest juz kontakt o takim numerku
            x = self[c.uin]
            self.data.remove(x) #usuwamy go wiec
            self.add_contact(c) #.. i tworzymy nowy :]
        else:
            self.data.append(c)
    
    def remove_contact(self, uin):
        """
        Metoda usuwajaca kontakt o numerze uin z listy. W przypadku, gdy na liscie nie ma kontaktu o podanym uin wyrzucany jest wyjatek KeyError.
        """
        contact = self[uin]
        if contact == None: 
            raise GGNotInContactsList(uin)
        else:
            self.data.remove(contact)

    def __index_by_uin(self, uin):
        """
        Znajduje miejsce w liscie kontaktow kontaktu u numerku 'uin'
        Zwraca:
            * miejsce w liscie kontaktow (jesli znaleziono)
            * -1 (jesli nie znaleziono)
        """
        i = 0
        for c in self.data:
            if int(c.uin) == int(uin):
                return i
            i += 1
        return -1
    
    def __getitem__(self, uin):
        """
        Zwraca:
            * kontakt o numerze uin, jesli taki jest na liscie kontaktow
            * None gdy nie ma takiego kontaktu na liscie
        """
        index = self.__index_by_uin(uin)
        if index == -1:
            return None
        else:
            return self.data[index]
    
    def __len__(self):
        return len(self.data)

    def __contains__(self, contact):
        """
        Sprawdza czy dany kontakt jest na liscie kontaktow
        parametr:
            * contact (typu Contact lub integer)
        uzycie:
            * if 3932154 in contacts_list:
                pass
            * c = Contact({"uin":423543, "shown_name":"Juzefina})
              if c in contacts_list:
                pass
        """
        if type(contact) == types.IntType:
            return self[contact] != None
        elif type(contact) == Contact:
            return self.data.__contains__(contact)
        else:
            raise AssertionError
    
    def export_request_string(self):
        """
        Metoda zwracajaca cala liste kontaktow w formacie pliku kontaktow Gadu-Gadu. Kazda linia reprezentuje jeden kontakt.
        """
        return "\n".join(map(Contact.request_string, self.data))
        
if __name__ == '__main__':
    test_str = 'Tola;;;Tola;;;12345;;0;;1;/home/user/message.wav;1;'
    c = Contact.from_request_string(test_str)
    assert (test_str == c.request_string())

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

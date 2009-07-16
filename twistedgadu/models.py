# -*- coding: utf-8
__author__="lreqc"
__date__ ="$2009-07-14 07:33:27$"

import hashlib, struct
from twistedgadu.comm.gadu_base import GGStruct_Notify

class UserProfile(object):

    def __init__(self, contacts={}, hashelem = None):
        self.uin = 0
        self.__hashelem = hashelem
        self.__contacts = contacts
        self.__connection = None
        
    def __set_password(self, value):
        self.__hashelem = hashlib.new('sha1')
        self.__hashelem.update(value)

    def __get_hashelem(self):
        return self.__hashelem.copy()

    password = property(__get_hashelem, __set_password)

    def update_contact(self, struct):
        pass

    def _creditials(self, result, *args, **kwargs):
        """Called by protocol, to get creditials, result will be passed to login
            procedure. It should be a 2-tuple with (uin, hash_elem)"""
        return self.onCreditialsNeeded()

    def _loginSuccess(self, conn, *args, **kwargs):
        self.__connecton = conn
        self.onLoginSuccess()
        return self

    # high-level interface
    @property
    def connected(self):
        """Is the profile currently used in an active connection"""
        return self.__connection is not None

    def putContact(self, contact):
        self.__contacts[contact.uin] = contact

        if self.connected:
            self.setNotifyState(contact.uin, contact.notify_flags)

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
    def onCreditialsNeeded(self, *args, **kwargs):
        return (self.uin, self.__hashelem)

    def onLoginSuccess(self):
        """Called when login is completed."""
        pass

    def onLoginFailure(self, reason):
        """Called after an unsuccessful login."""
        pass

    def onContactStatusChange(self, contact):
        """Called when a status of a contact has changed."""
        pass

    def onMessageReceived(self, message):
        """Called when a message had been received"""
        pass

    def itercontacts(self):
        return self.__contacts.iteritems()

class Def(object):
    def __init__(self, type, default_value, required=False, exportable=True):
        self.type = type
        self.default = default_value
        self.required = required
        self.exportable = exportable
        
def mkdef(*args):
    return Def(*args) 

class Contact(object):
    """Single contact as seen in catalog (person we are watching) - conforming to GG8.0"""

    DEFAULTS = {
        'Guid':             mkdef(str, '', True),
        'GGNumber':         mkdef(str, '', True),
        'ShowName':         mkdef(str, '', True),
        'MobilePhone':      mkdef(str, ''),
        'HomePhone':        mkdef(str, ''),
        'Email':            mkdef(str, 'someone@somewhere.moc'),
        'WWWAddress':       mkdef(str, ''),
        'FirstName':        mkdef(str, ''),
        'LastName':         mkdef(str, ''),
        'Gender':           mkdef(int, 0),
        'Birth':            mkdef(str, ''),
        'City':             mkdef(str, ''),
        'Province':         mkdef(str, ''),
        'Groups':           mkdef(list, ['0']),
        'CurrentAvatar':    mkdef(int, 0),
        'Avatars':          mkdef(list, []),
        'UserActivatedInMG':mkdef(bool, False),
        'FlagBuddy':        mkdef(bool, False),
        'FlagNormal':       mkdef(bool, False),
        'FlagFriend':       mkdef(bool, False),
        'FlagIgnored':      mkdef(bool, False),
        # state variables
        'description':      mkdef(str, '', False, False),
        'status':           mkdef(int, 0, False, False),
    }

    @classmethod
    def simple_make(cls, profile, uin, name):
        return cls(profile, Guid=str(uin), GGNumber=str(uin), ShowName=name)

    def __init__(self, profile, **kwargs):

        for (k, v) in self.DEFAULTS.iteritems():
            if v.required and not kwargs.has_key(k):
                raise ValueError("You must supply a %s field." % k)

            setattr(self, k, kwargs.get(k, v.default))
            if not isinstance(getattr(self, k), v.type):
                raise ValueError("Field %s has to be of class %s." % (k, v.type.__name__)) 


    @property
    def uin(self):
        return self.GGNumber

    @property
    def notify_flags(self):
        return int(self.FlagBuddy and GGStruct_Notify.BUDDY) \
            & int(self.FlagFriend and GGStruct_Notify.FRIEND) \
            & int(self.FlagIgnore and GGStruct_Notify.IGNORE)

    def exportToXML(self):
        pass

    def updateStatus(self, status, desc=None):
        self.status = status
        if desc: self.description = desc

#     @classmethod
#     def from_request_string(cls, rqs):
#         dict = {}
#         for (fmt, value) in zip(cls.RQ_STRING_FORMAT, rqs.split(';')):
#             dict[fmt[0]] = fmt[1](value)
#         return cls(**dict)
# 
#     def request_string(self):
#         return ";".join( [ str(self.__getattribute__(fmt[0])) for fmt in self.RQ_STRING_FORMAT] )

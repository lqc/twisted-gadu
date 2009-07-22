#!/usr/bin/env python
# -*- coding: utf-8

__author__ = "Łukasz Rekucki"
__date__ = "$2009-07-19 09:50:34$"

from lqsoft.cstruct.common import CField
from lqsoft.cstruct.constraints import *

def string_padder(opts):
    pad = opts['padding']
    opts['value'] += pad*'\x00'

class StringField(CField):    
    KEYWORDS = dict(CField.KEYWORDS,
        length= lambda lv: LengthConstraint(\
            length=lv, padding_func=string_padder) )

    def __init__(self, idx, default='', length=0, **kwargs):
        CField.__init__(self, idx, default, **dict(kwargs, length=length) )
        
    def _format_string(self, opts):
        return '<'+str(opts['length'])+'s'

    def _retrieve_value(self, opts):
         (v, offset) = CField._retrieve_value(self, opts)
         return (v[0], offset)

  
class NullStringField(CField):

    def _format_string(self, opts):
        return '<'+str(opts['length'])+'s'

    def before_unpack(self, opts):
        CField.before_unpack(self, opts)
        try:
            opts['length'] = opts['data'].index('\0', opts['offset']) - opts['offset']
        except ValueError:
            raise UnpackError("Unterminated null string occured.")

    def before_pack(self, obj, offset, **opts):
        value = getattr(obj, self.name)
        return CField.before_pack(self,obj, offset, length=len(value), **opts)

    def pack(self, obj, offset, **opts):
        value = getattr(obj, self.name)
        return CField.pack(self, obj, offset, length=len(value), **opts)

    def _retrieve_value(self, opts):
        (v, offset) = CField._retrieve_value(self, opts)
        return (v[0], offset)

    def set_value(self, obj, value):
        if not isinstance(value, str) or value[-1] != '\0':
            raise ValueError("NullStringField value must a string with last character == '\\0'.")
        
        return CField.set_value(self, obj, value)
#!/usr/bin/env python
# -*- coding: utf-8

__author__ = "Łukasz Rekucki"
__date__ = "$2009-07-19 07:46:52$"

from lqsoft.cstruct.common import ListItemWrapper, CField
from lqsoft.cstruct.constraints import *


def array_padder(opts):
    pad = opts['padding']
    opts['value']._extend(None for _ in xrange(0, pad))
    # setattr(opts['obj'], '_' + opts['field'].name, value)

class ArrayField(CField):
    KEYWORDS = dict(CField.KEYWORDS,
        length= lambda lv: LengthConstraint(\
            length=lv, padding_func=array_padder) )

    def __init__(self, idx, subfield, default=[], length=0, **kwargs):
        CField.__init__(self, idx, default, **dict(kwargs, length=length) )
        self.__subfield = subfield

    # packing
    def before_pack(self, obj, offset, **opts):
        value = getattr(obj, self.name)

        if (value == None) and self.nullable:
            return 0 # field is ommit

        opts.update({'field': self, 'obj': obj, 'value': value})
        for c in reversed(self.constraints):
            c.before_pack(opts)     

        data_len = 0
        off = offset
        for i in xrange(0, opts['length']):
            # map the field to index i
            self.__subfield.name = str(i)
            sf_len = self.__subfield.before_pack(value, off)
            data_len += sf_len
            off += sf_len

        return data_len

    def pack(self, obj, offset, **opts):
        value = getattr(obj, self.name)

        if (value == None) and self.nullable:
            return '' # field is ommit

        opts.update({'field': self, 'obj': obj, 'value': value})
        for c in reversed(self.constraints):
            c.pack(opts)

        # all constraints to this field applied      

        buffer = ''
        off = offset
        for i in xrange(0, opts['length']):
            # map the field to index i
            self.__subfield.name = str(i)
            data = self.__subfield.pack(value, off)
            off += len(data)
            buffer += data
        return buffer


    # unpacking
    def _retrieve_value(self, opts):
        l = []
        offset = opts['offset']

        for i in xrange(0, opts['length']):
            self.__subfield.name = str(i)
            v, offset = self.__subfield.unpack(opts['obj'], opts['data'], offset)
            l.append(v)            
        return (l, offset)

    def item_set_value(self, wrapper, item_name, new_value):
        # let the subfield se the value - this validates
        # print self, wrapper, item_name, new_value
        self.__subfield.name = item_name
        return self.__subfield.set_value(wrapper, new_value)

    def item_get_value(self, wrapper, item_name, current_value):
        # let the subfield se the value - this validates
        self.__subfield.name = item_name
        return self.__subfield.get_value(wrapper, current_value)

    # override set, to wrap the value
    def set_value(self, obj, value):
        wrapper = ListItemWrapper(value)
        wrapper._set_action = self.item_set_value
        wrapper._get_action = self.item_get_value
        return CField.set_value(self, obj, wrapper)

    # no need to wrap the get
    

class StructInline(CField):
    def __init__(self, idx, default=None, **kwargs):
        CField.__init__(self, idx, default, **kwargs)
        self.struct_class = kwargs.get('struct')

    def pack(self, value):
        return value.pack()

    def unpack(self, data):
        return self.struct_class.unpack(data)

    def validate(self, value):
        CField.validate(self, value)

        if not isinstance(value, self.struct_class):
            raise ValueError('StructInline must contain a structures of class %s.' \
                    % self.struct_class.__name__ )

        return value


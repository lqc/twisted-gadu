# -*- coding: utf-8
from lqsoft.cstruct.fields import CField

class MetaStruct(type):
    def __new__(cls, name, bases, cdict):             
        fields = []
        internal_dict = {}
        ndict = {}
        # log('Constructing class: ' + name)

        for (field_name, field_value) in cdict.iteritems():
            if isinstance(field_value, CField):               
                field_value.name = field_name
                fields.append(field_value)
                internal_dict[field_name] = field_value
                ndict[field_name] = property( \
                    MetaStruct.getter_for(field_name), \
                    MetaStruct.setter_for(field_name) )
            else:
                ndict[field_name] = field_value
        
        klass = type.__new__(cls, name, bases, ndict)
        
        old_dict = getattr(klass, '_internal', {})        
        internal_dict.update(old_dict)
        setattr(klass, '_internal', internal_dict)

        fields.sort(key= lambda item: item.idx)

        order = getattr(klass, '_field_order', [])        
        order = order + fields
        setattr(klass, '_field_order', order)        
        return klass


    @staticmethod
    def getter_for(name):
        def getter(self):
            # log("Called getter on %r with %r" % (self, name))
            return getattr(self, '_'+ name)
        return getter

    @staticmethod
    def setter_for(name):
        def setter(self, value):
            # log("Called setter on %r with %r" % (self, name))
            return setattr(self, '_' + name, value)
        return setter
        
class CStruct(object):
    __metaclass__ = MetaStruct

    def __init__(self, **kwargs):       
        for field in self._field_order:                        
            setattr(self, '_' + field.name, field._validate(self, kwargs[field.name]) )

    def pack(self):
        s = ''
        for field in self._field_order:            
            s += field.pack( getattr(self, '_' + field.name) )
        return s

    @classmethod
    def unpack(cls, data, offset=0):
        print "Unpacking class: " + cls.__name__        
        dict = {}

        for field in cls._field_order:
            print "Unpacking field: " + field.name
            value, next_offset = field.unpack(dict, data, offset)
            dict[field.name] = value
            offset = next_offset            
             
        return cls(**dict), offset

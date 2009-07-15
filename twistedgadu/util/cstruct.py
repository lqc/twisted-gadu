# -*- coding: utf-8
import struct

class CField(object):    
    def __init__(self, idx):
        self.idx = idx
        self.default = None
        
    def pack(self, value):
        return ''

    def unpack(self, data):
        return None, data

    def extract(self, kwargs):
        if not kwargs.has_key(self.name) and self.default is None:
            raise ValueError("You must pass a legal value for field %s." % self.name)
        
        return kwargs.get(self.name, self.default)

    def validate(self, value):
        return value

    def __repr__(self):
        return self.name + '[' + self.ctype() + ']'

class NumericField(CField):
    def __init__(self, idx, unsigned=False, default=0):
        CField.__init__(self, idx)
        self.unsigned = unsigned
        self.default = default

    def _fmt(self):
        pass
    
    def unpack(self, data):
        fmt = self._fmt()
        dlen = struct.calcsize(fmt)
        value = struct.unpack_from(fmt, data, 0)
        return (value[0], data[dlen:])

    def pack(self, value):
        return struct.pack(self._fmt(), value )

    def extract(self, kwargs):
        return int( CField.extract(self, kwargs) )
    
    def validate(self, value):
        if not isinstance(value, int):
            raise ValueError('Field %s can only hold numeric values.' % self.name)

        return value

class IntField(NumericField):
    def _fmt(self):
        return '<'+(self.unsigned and 'I' or 'i')

class ShortField(NumericField):
    def _fmt(self):
        return '<'+(self.unsigned and 'H' or 'h')

class ByteField(NumericField):
    def _fmt(self):
        return '<'+(self.unsigned and 'B' or 'b')
        
class StringField(CField):
    def __init__(self, idx, length, default=''):
        CField.__init__(self, idx)
        self.length = length
        self.default = default

    def _fmt(self):
        return '<'+str(self.length)+'s'

    def unpack(self, data):
        value = struct.unpack_from(self._fmt(), data, 0)
        return (value[0], data[self.length:])

    def pack(self, value):
        return struct.pack(self._fmt(), value)

    def extract(self, kwargs):
        return str( CField.extract(self, kwargs) )

    def validate(self, value):
        if not isinstance(value, str):
            raise ValueError('Field %s can only hold string values.' % self.name)

        if len(value) > self.length:
            raise ValueError('Field %s can only hold %d characters.' %(self.name, self.length))

        return value
        

class NullStringField(CField):
    def __init__(self, idx, default=''):
        CField.__init__(self, idx)
        self.default = default

    def pack(self, value):
        return struct.pack(str(len(value))+"s", value) + chr(0)

    def unpack(self, data):
        offset = 0

        while offset < len(data) and ord(data[offset]) != 0:
            offset += 1

        if offset == len(data):
            raise ValueError("Couldn't unpack NULL terminated string from: %r" % data)

        return (str(data[:offset+1]), data[offset+1:])

class VarcharField(CField):
    def __init__(self, idx, default=''):
        CField.__init__(self, idx)
        self.default = default

    def unpack(self, data):
        length = struct.unpack_from("<I", data, 0)[0]
        value = struct.unpack_from('<'+str(length)+'s', data, 4)
        return (value[0], data[length+4:])

    def pack(self, value):
        l = len(value)
        return struct.pack('<I'+str(l)+'s', l, value)

    def extract(self, kwargs):
        return str( CField.extract(self, kwargs) )

    def validate(self, value):
        if not isinstance(value, str):
            raise ValueError('Field %s can only hold string values.' % self.name)

        return value

class StructArray(CField):
    def __init__(self, idx, struct_class, default=[]):
        CField.__init__(self, idx)
        self.struct_class = struct_class
        self.default = default

    def pack(self, vlist):
        buf = ''
        for v in vlist:
            buf += v.pack()
        return buf

    def unpack(self, data):
        offset = 0
        raw = data
        vlist = []

        while len(raw) > 0:
            v, raw = self.struct_class.unpack(raw)
            vlist.append(v)

        return vlist, raw # raw should be 0

    def validate(self, vlist):
        CField.validate(self, vlist)
        
        if not isinstance(vlist, list):
            raise ValueError('StructArray must contain a list of structures.')

        for value in vlist:
            if not isinstance(value, self.struct_class):
                raise ValueError('StructArray must contain a list of structures of class %s.' \
                    % self.struct_class.__name__ )

        return vlist

class StructInline(CField):
    def __init__(self, idx, struct_class, default=None):
        CField.__init__(self, idx)
        self.struct_class = struct_class
        self.default = default

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

def log(str):
    sys.stderr.write( repr(str) + '\n')
        
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
            setattr(self, '_' + field.name, field.validate( field.extract(kwargs)) )

    def pack(self):
        s = ''
        for field in self._field_order:
            s += field.pack( getattr(self, '_' + field.name) )
        return s

    @classmethod
    def unpack(cls, data):
        print "Unpacking class: " + cls.__name__
        dict = {}
        for field in cls._field_order:
            dict[field.name], data = field.unpack(data)
        return cls(**dict), data
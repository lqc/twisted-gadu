# -*- coding: utf-8

import lqsoft.cstruct.constraints as const

class CField(object):    
    def __init__(self, idx, default=None, **kwargs):
        self.idx = idx
        self.default = default
        self.constraints = {
            'offset': const.OffsetConstraint(kwargs['offset']),
            'prefix': const.PrefixConstraint(kwargs['prefix']),
            'ommit': const.FunctionConstraint(kwargs['only_f']),
        }
        
    def _check_prefix(self, data, pos):
        cpos = pos
        for char in prefix:
            if cpos >= len(data): # prefix exceeds the data 
                return False
            if data[cpos] != char: # characters don't match
                return False
            cpos += 1
        return True

    def _get_offset(self):
        """Returns a function, which applied to an instance, 
            returns this field's offset field value"""
        if isinstance(self.offset, int):
            return lambda _: self.offset
        
        if isinstance(self.offset, str):
            if not self.parent:
                raise ValueError("Offset of the fields is attached,\
                    but no parent structure assigned")
            off_field = getattr(self.parent, self.offset)
            if not isinstance(off_field, NumericField):
                raise ValueError("Field offset can only be attached \
                    to a numeric field.")
            return lambda instance: getattr(instance, self.offset)

    def pack(self, value):
        return ''

    def unpack(self, instance, data, pos):
        """We have two method chains here:
            * first are methods that modify constraints about how the value should be unpacked.
            * second is methods that modify the retrieved value. 
        """
        constraints = dict(self.constraints)
        self._check_constraints(instance, data, pos, constraints)

        (value, new_pos) = self._retrieve_value(data, pos, constraints)

        return (self._validate(value), new_pos)

    def 





        self.
        def _cont(instance, data, pos):
            if not self.condition(instance, data, pos) \
            and not self._check_prefix(data, pos):
                return (self.default, pos)

            return next(instance, data, pos)

        return _cont

    def extract(self, kwargs):
        if not kwargs.has_key(self.name) and self.default is None:
            raise ValueError("You must pass a legal value for field %s." % self.name)
        
        return kwargs.get(self.name, self.default)

    def validate(self, value):
        return value

    def __repr__(self):
        return self.name + '[' + self.ctype() + ']'

class NumericField(CField):
    def __init__(self, idx, default=0, **kwargs):
        CField.__init__(self, idx, default, **kwargs)
        self.unsigned = kwargs.get('unsigned', False)

    def _fmt(self):
        pass
    
    def unpack(self, next):
        """self - concrete definition of the field
           inst - intance of a CStruct - contains already unpacked values"""  

        def _cont(instance, data, pos):
            fmt = self._fmt()
            dlen = struct.calcsize(fmt)
            value = struct.unpack_from(fmt, data, pos)
            return (value[0], pos+dlen)

        return CField.unpack(self, _cont)
        


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
    def __init__(self, idx, default='', **kwargs):
        CField.__init__(self, idx, default, **kwargs)
        self.length = kwargs.get('length')

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
    def __init__(self, idx, default='', **kwargs):
        CField.__init__(self, idx, default, **kwargs)

    def pack(self, value):
        return struct.pack(str(len(value))+"s", value) + chr(0)

    def unpack(self, data):
        offset = 0

        while offset < len(data) and ord(data[offset]) != 0:
            offset += 1

#        if offset == len(data):
#            raise ValueError("Couldn't unpack NULL terminated string from: %r" % data)

        return (str(data[:offset+1]), data[offset+1:])

class VarcharField(CField):
    def __init__(self, idx, default='', **kwargs):
        CField.__init__(self, idx, default, **kwargs)

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

class ArrayField(CField):
    def __init__(self, idx, default=[], **kwargs):
        CField.__init__(self, idx, default, **kwargs)
        self.packable_class = kwargs.get('klass')

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


# -*- coding: utf-8

def nop(self, *args, **kwargs):
    return True

# default priorities
PRIO_OFFSET = 100
PRIO_PREFIX = 500
PRIO_TYPE = 600
PRIO_LENGTH = 700
PRIO_NBOUNDS = 800

class IConstraint(object):
    def __init__(self, priority):
        self.priority = priority

    def __str__(self):
        return self.__class__.__name__

    def before_unpack(self, opts):
        return True

    def pack(self, opts):
        return True

    def before_pack(self, opts):
        return True

    def on_value_set(self, opts):
        pass
    
class PrefixConstraint(IConstraint):
    def __init__(self, param, priority=PRIO_PREFIX):
        IConstraint.__init__(self, priority)

        if not isinstance(param, str):
            raise ValueError("Prefix constraints takes a byte array as an argument")
        self.prefix = param

    def match(self, data, pos):
        l = len(data)
        for char in self.prefix:
            if pos >= l: # prefix exceeds the data
                return False

            if data[pos] != char: # characters don't match
                return False
            pos += 1
        return True

    def before_unpack(self, opts):
        return self.match(opts['data'], opts['offset'])

class OffsetConstraint(IConstraint):

    def __init__(self, param, priority=PRIO_OFFSET):
        IConstraint.__init__(self, priority)

        if isinstance(param, str):
            self.before_upack = self.before_upack_field
        elif isinstance(param, int):
            self.before_upack = self.before_upack_number
        else:
            raise ValueError("Offset constraint must contain a number or a valid field name.")
        
        self.__offset = param

    def before_upack_number(self, options):
        if self.__offset != options['offset']:
            return False
        return True

    def before_upack_field(self, options):
        off_field = getattr(options['obj'], self.__offset)
        if not isinstance(off_field, NumericField):
            raise ValueError("Field offset can only be attached \
                    to a numeric field.")
        if getattr(options['obj'], self.__offset) != options['offset']:
            return False
        return True      

    def before_pack(self, options):       
        if isinstance(self.__offset, str):           
            setattr(options['obj'], self.__offset, options['offset'])
            
    def pack(self, options):
        if isinstance(self.__offset, int) and (options['offset'] != self.__offset):
            raise PackingException("Explicit offset of field %s was set, but position doesn't match" % \
                options['field'].name )
            
class ValueTypeConstraint(IConstraint):

    def __init__(self, typeklass, priority=PRIO_TYPE):
        IConstraint.__init__(self, priority)

        if not isinstance(typeklass, type):
            raise ValueError("This constraint must contain a type class.")
        self._klass = typeklass

    def on_value_set(self, opts):
        if not isinstance(opts['value'], self._klass):
            raise ValueError("Field %s accepts only instances of %s as value."\
                % (opts['field'].name, self._klass.__name__) )

class NumericBounds(IConstraint):
    BOUND_FOR_CTYPE = {
        'int':      (-(2**31)+1 , 2**31),
        'uint':     (0          , 2**32-1),
        'short':    (-(2**15)+1 , 2**15),
        'ushort':   (0          , 2**16-1),
        'byte':     (-127, 128),
        'ubyte':    (0, 255),
    }

    def __init__(self, lower_bound = None, upper_bound = None, ctype=None, \
      priority=PRIO_NBOUNDS):
        IConstraint.__init__(self, priority)

        if ctype != None:
            self._lbound, self._ubound = self.BOUND_FOR_CTYPE[ctype]
        elif lower_bound == None or upper_bound == None:
            raise ValueError("You need to specify bounds or a ctype.")
        else:
            self._lbound = lower_bound
            self._ubound = upper_bound

    def on_value_set(self, opts):
        if not (self._lbound <= opts['value'] <= self._ubound):
            raise ValueError("Field %s - value %s out of bounds."\
                % (opts['field'].name, opts['value']) )

class LengthConstraint(IConstraint):
    def __init__(self, length, padding_func, priority=PRIO_LENGTH):
        IConstraint.__init__(self, priority)

        if isinstance(length, str):
            self.before_unpack = self.before_unpack_field
        elif isinstance(length, int):
            self.before_unpack = self.before_unpack_number
        else:
            raise ValueError("Length constraint must contain a number or a field name.")

        self.__length = length
        self.__padding_func = padding_func

    def on_value_set(self, opts):
        L = len(opts['value'])
        if isinstance(self.__length, str):            
            setattr(opts['obj'], self.__length, L)
        elif L > self.__length:
            raise ValueError("Field %s has limited length of %d." % (opts['field'].name, self.__length) )
        else:
            opts['padding'] = (self.__length - L)
            self.__padding_func(opts)

    def before_pack(self, opts):
        # the value is about to be packed
        # nothing to do here, 'cause we ensure proper length in the trigger
        opts['length'] = len(opts['value'])

    def pack(self, opts):
        # value is being packed - add our property
        opts['length'] = len(opts['value'])

    def before_unpack_number(self, opts):
        opts['length'] = self.__length            
        return True

    def before_unpack_field(self, opts):
        opts['length'] = getattr(opts['obj'], self.__length)
        return True

    def validate(self, obj, value):
        if isinstance(value, str) and isinstance(self.__length, int) \
         and len(value) > self.__length:
            return False
        return True
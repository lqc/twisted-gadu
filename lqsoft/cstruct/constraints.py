# -*- coding: utf-8


class IConstraint(object):    
    def __str__(self):
        return self.__class__.__name__

    def apply(self, opts):
        return True

    def validate(self, value):
        return True

    def evaluate(self, ops):
        return True
    
class PrefixConstraint(IConstraint):

    def __init__(self, param):
        if not isinstance(param, str):
            raise ValueError("Prefix constraints takes a byte array as an argument")
        self.prefix = param

    def apply(self, options):
        i = options['offset']
        l = len(options['data'])
        for char in self.prefix:
            if i >= l: # prefix exceeds the data
                return False

            if options['data'][i] != char: # characters don't match
                return False
            i += 1
        return True

class OffsetConstraint(IConstraint):

    def __init__(self, param):
        if isinstance(param, str):
            self.apply = _apply_field
        elif isinstance(param, int):
            self.apply = _apply_number
        else:
            raise ValueError("Offset constraint must contain a number or a valid field name.")
        
        self.__offset = param

    def _apply_number(self, options):
        if self.__offset != options['offset']:
            return False
        return True

    def _apply_field(self, options):
        off_field = getattr(options['dict'], self.__offset)
        if not isinstance(off_field, NumericField):
            raise ValueError("Field offset can only be attached \
                    to a numeric field.")
        if getattr(options['dict'], self.__offset) != options['offset']:
            return False
        return True      

    def evaluate(self, options):
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

class ValueTypeConstraint(IConstraint):

    def __init__(self, typeklass):
        if not isinstance(typeklass, type):
            raise ValueError("This constraint must contain a type class.")
        self._klass = typeklass

    def validate(self, value):
        return isinstance(value, self._klass)

class NumericBounds(IConstraint):
    BOUND_FOR_CTYPE = {
        'int':      (-(2**31)+1 , 2**31),
        'uint':     (0          , 2**32-1),
        'short':    (-(2**15)+1 , 2**15),
        'ushort':   (0          , 2**16-1),
        'byte':     (-127, 128),
        'ubyte':    (0, 255),
    }

    def __init__(self, lower_bound = None, upper_bound = None, ctype=None):
        if ctype != None:
            self._lbound, self._ubound = self.BOUND_FOR_CTYPE[ctype]
        elif lower_bound == None or upper_bound == None:
            raise ValueError("You need to specify bounds or a ctype.")
        else:
            self._lbound = lower_bound
            self._ubound = upper_bound

    def validate(self, value):
        return (self._lbound <= value <= self._ubound)

class LengthConstraint(IConstraint):

    def __init__(self, param):
        if isinstance(param, str):
            self.apply = _apply_field
        elif isinstance(param, int):
            self.apply = _apply_number
        else:
            raise ValueError("Length constraint must contain a number or a valid field name.")

        self.__length = param


    def _apply_number(self, opts):
        opts['length'] = self.__length            
        return True

    def _apply_field(self, options):
        off_field = getattr(options['dict'], self.__offset)
        if not isinstance(off_field, NumericField):
            raise ValueError("Field length can only be attached \
                    to a numeric field.")                    
        opts['length'] = self.__length
        return True

    def validate(self, struct, value):
        return
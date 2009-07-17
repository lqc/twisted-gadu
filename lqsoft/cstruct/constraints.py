# -*- coding: utf-8

class PrefixConstraint(object):

    def __init__(self, param):
        if not isinstance(param, str):
            raise ValueError("Prefix constraints takes a byte array as an argument")


    def apply(self, instance, data, offset):





        : 
cpos = pos
        for char in prefix:
            if cpos >= len(data): # prefix exceeds the data 
                return False
            if data[cpos] != char: # characters don't match
                return False
            cpos += 1
        return True


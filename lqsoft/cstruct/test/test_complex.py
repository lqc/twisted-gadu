#!/usr/bin/env python
# -*- coding: utf-8

import unittest
import struct

from lqsoft.cstruct.common import CStruct
from lqsoft.cstruct.fields.complex import *
from lqsoft.cstruct.fields.numeric import IntField
from lqsoft.cstruct.constraints import *

__author__="lreqc"
__date__ ="$2009-07-21 00:43:44$"

class ArrayFieldTest(unittest.TestCase):

    def setUp(self):
        self.svalue = [1,1,2,3,5,8]
        self.slen = len(self.svalue)
        self.sdata = struct.pack("<"+str(self.slen)+"i", *self.svalue)
        # self.sdata_ext = struct.pack("<I", self.slen) + self.sdata

    def testArrayPack(self):
        class TestStruct(CStruct):
            array = ArrayField(0, length = self.slen, subfield=IntField(0))

        s = TestStruct(array=self.svalue)
        try:
            s.array[1] = 'ala ma kota' # this should fail
            self.fail('Integer array accepted a string')
        except ValueError:
            pass

        self.assertEqual( s.array , self.svalue)
        self.assertEqual( s.pack(), self.sdata)

    def testArrayUnpack(self):
        class TestStruct(CStruct):
            array = ArrayField(0, length = self.slen, subfield=IntField(0))

        s, offset = TestStruct.unpack(self.sdata)

        self.assertEqual(s.array, self.svalue)
        for i in xrange(0, self.slen):
            self.assertEqual( s.array[i], self.svalue[i])
        
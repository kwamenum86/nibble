#!/usr/bin/python -u

import os
import sys
sys.path.insert(0,  os.path.normpath(os.path.join(__file__, '../..')));
from nibble import Writer

filepath = "wbytes.bin"

test_suite = []

def test_func(fn):
	def _fn():
		print "%s:" % fn.__doc__
		res = fn()
		print (res and "Success" or "Failed") + "\n"
	test_suite.append(_fn)
	return _fn

@test_func
def test():
	"""Basic test to ensure that writing 5 bits at a time works as expected"""
	n = Writer(filepath)
	data_good = True
	test_bytes = [74, 82, 144]
	byte_index = 0
	n.put([9, 9, 9, 9], item_size=5)
	n.close()
	fh = open(filepath, "rb")
	for byte in fh.read():
		data_good &= ord(byte) == test_bytes[byte_index]
		if not data_good:
			break
		byte_index += 1
	fh.close()
	os.remove(filepath)
	return data_good

@test_func
def test():
	"""Ensure that calling the buffer is not "flushed" between put calls"""
	n = Writer(filepath)
	byte_count = 0
	n.put([9, 9], item_size=5)
	n.put([9, 9], item_size=5)
	n._flush_buffer()
	n.close()
	fh = open(filepath, "rb")
	for byte in fh.read():
		byte_count += 1
	fh.close()
	os.remove(filepath)
	return byte_count == 3

if __name__ == "__main__":
	for test in test_suite:
		test()

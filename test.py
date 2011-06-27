import os
from nibble import Writer

filepath = "wbytes.bin"

test_suite = []

def test_func(fn):
	def _fn():
		print "Performing '%s' test:" % fn.__doc__
		res = fn()
		print (res and "Success" or "Failed") + "\n"
	test_suite.append(_fn)
	return _fn

@test_func
def test():
	"""Really weak"""
	n = Writer(filepath)
	data_good = True
	n.write([9, 9, 9, 9], item_size=4)
	n.close()
	fh = open(filepath, "rb")
	for byte in fh.read():
		data_good &= ord(byte) == 153
		if not data_good:
			break
	fh.close()
	os.remove(filepath)
	return data_good

@test_func
def test():
	"""file_func"""
	n = Writer(filepath)
	byte_count = 0
	n.write([9, 9], item_size=4)
	n.close()
	n.write([9, 9], item_size=4)
	n.close()
	fh = open(filepath, "rb")
	for byte in fh.read():
		byte_count += 1
	fh.close()
	os.remove(filepath)
	return byte_count == 2

if __name__ == "__main__":
	for test in test_suite:
		test()

import os
from nibble import Writer

filepath = "wbytes.bin"

test_suite = []

def test_func(fn):
	def _fn():
		print "Performing test '%s':" % fn.__doc__
		print fn() + "\n"
	test_suite.append(_fn)
	return _fn

@test_func
def test_1():
	"""Really weak test"""
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
	if data_good:
		return "Success"
	else:
		return "Data corrupted"

if __name__ == "__main__":
	for test in test_suite:
		test()

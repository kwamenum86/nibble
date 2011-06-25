import os
from nibble import Nibble

filepath = "wbytes.bin"

def test_1():
	"""Really weak test"""
	n = Nibble(filepath)
	data_good = True
	n.write_items([9, 9, 9, 9], item_size=4)
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
	print "Performing test '%s':" % test_1.__doc__
	print test_1() + "\n"

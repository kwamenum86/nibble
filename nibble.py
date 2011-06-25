import math

class Nibble():
	@staticmethod
	def iter_bytes(num):
		while num:
			yield num & 255
			num >>= 8

	def __init__(self, filename):
		# item length in bits
		self.fh = None
		self.filename = filename

	def write_items(self, items, item_fn = None, item_size = None):
		buffer = 1
		if self.fh is None:
			self.fh = open(self.filename, "wb")
		for item in items:
			data = item_fn and item_fn(item) or item
			for byte in Nibble.iter_bytes(data):
				buffer <<= item_size or num_digits(byte, 2)
				buffer |= byte
				# Can't flush the buffer at 8 because of the dummy digit
				digits = num_digits(buffer, 2)
				if  digits > 8:
					# extract digits 2 through 9 i.e. a byte's worth of bits offset by 1
					# to account for the dummy digit
					offset = digits - 9
					out = (buffer & 255 << offset) >> offset
					# Keep the remaining bits plus a dummy digit
					if digits == 9:
						buffer = 1
					else:
						buffer = buffer & ones(offset) | (1 << offset)
					self.fh.write("%c" % out)
		if buffer > 1:
			buffer <<= 9 - num_digits(buffer, 2)
			out = buffer & 255
			self.fh.write("%c" % out)
		self.fh.close()

def ones(num):
	val = 1
	num -= 1
	while num:
		val <<= 1
		val += 1
		num -= 1
	return val

def pad_pls(number, rightPadding = False):
	str = bin(number)[2:]
	return (rightPadding and str or "") + ("0" * (8 - len(str))) + (not rightPadding and str or "")

def num_digits(number, base):
	return int(math.floor(math.log(number) / math.log(base)) + 1)

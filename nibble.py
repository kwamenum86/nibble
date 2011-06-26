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
		buffer_size = 0
		if self.fh is None or self.fh.closed:
			self.fh = open(self.filename, "wb")
		for item in items:
			data = item_fn and item_fn(item) or item
			for byte in Nibble.iter_bytes(data):
				# TODO figure out how to get rid of num_digits here
				shift_count = item_size or num_digits(byte, 2)
				buffer <<= shift_count
				buffer_size += shift_count
				buffer |= byte
				# Can't flush the buffer at 8 because of the dummy digit
				if  buffer_size > 7:
					# extract digits 2 through 9 i.e. a byte's worth of bits offset by 1
					# to account for the dummy digit
					offset = buffer_size - 8
					out = (buffer & 255 << offset) >> offset
					# Keep the remaining bits plus a dummy digit.  The first code path below
					# is functionally equivalent to the second when buffer_size == 9.
					if buffer_size == 8:
						buffer = 1
						buffer_size = 0
					else:
						# (255 >> (8 - offset)) gives us the number represented by
						# *offset* ones digits.  For example, when offset is 2 output is 3.
						# The statement below is meant to reduce the buffer to bits that
						# have not been written yet.
						buffer = buffer & (255 >> (8 - offset)) | (1 << offset)
						buffer_size = offset
					self.fh.write("%c" % out)
		if buffer > 1:
			buffer <<= 9 - buffer_size
			out = buffer & 255
			self.fh.write("%c" % out)

	def close(self):
		if self.fh is None:
			return
		self.fh.close()

def num_digits(number, base):
	return int(math.floor(math.log(number) / math.log(base)) + 1)

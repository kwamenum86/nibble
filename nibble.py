import math

class FileClient():
	def __init__(self, filename):
		# item length in bits
		self.fh = None
		self.filename = filename
		self.buffer = None
		self.buffer_size = 0

	def close(self):
		if self.fh is None:
			return
		self.fh.close()

	@staticmethod
	def buffer_bits(byte, buffer, buffer_size, item_size):
		out = None
		buffer <<= item_size
		buffer_size += item_size
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
				buffer &= (255 >> (8 - offset))
				buffer |= (1 << offset)
				buffer_size = offset
		return buffer, buffer_size, out

	@staticmethod
	def file_func(mode):
		def _dec(fn):
			def _fn(self, *args, **kwargs):
				if self.fh is None or self.fh.closed:
					self.fh = open(self.filename, mode)
				return fn(self, *args, **kwargs)
			return _fn
		return _dec

class Writer(FileClient):
	# Data is not guaranteed to be in the file after calling put
	@FileClient.file_func("ab")
	def put_data(self, data, item_size = None):
		self.buffer = 1
		for byte in iter_bytes(data):
			# TODO figure out how to get rid of num_digits here
			self.buffer, self.buffer_size, out = FileClient.buffer_bits(byte, self.buffer, self.buffer_size, item_size or num_digits(byte, 2))
			if not out is None:
				self.fh.write("%c" % out)

	def _flush_buffer(self):
		if self.buffer > 1:
			self.buffer <<= 8 - self.buffer_size
			out = self.buffer & 255
			self.fh.write("%c" % out)

class Reader(FileClient):
	# offset is a tuple containing a byte offset and a bit offset
	# byte is a byte offset in the file
	# bit is an in offset in the file
	# both byte and bit are used to determine where to start reading
	@FileClient.file_func("rb")
	def get_data(self, byte = 0, bit = 0, size = 8):
		data = []
		buffer = 1
		buffer_size = 0
		# Normalize. bit should be less than 8
		byte += bit / 8
		bit = bit % 8
		self.fh.seek(byte)
		extra_bits = size - bit
		right_extra_bits = (size - bit) % 8
		# How many bytes to we need to pull to fulfill the request for `size` bits
		if size <= 8 - bit:
			bytes_to_read = 1
		else:
			bytes_to_read = extra_bits / 8 + 1
			if right_extra_bits:
				bytes_to_read += 1
		raw_bytes = self.fh.read(bytes_to_read)
		extracted = (255 >> bit) & ord(raw_bytes[0])
		buffer, buffer_size, out = FileClient.buffer_bits(extracted, buffer, buffer_size, 8 - bit)
		if not out is None:
			data.append(out)
		for byte in raw_bytes[1:-1]:
			buffer, buffer_size, out = FileClient.buffer_bits(ord(byte), buffer, buffer_size, 8)
			if not out is None:
				data.append(out)
		if len(raw_bytes) > 1:
			# Extract the first right_extra_bits from the last byte in raw_bytes.  Pad left with 0s
			extraction_mask = 255 & (1 << right_extra_bits + 1)
			extracted = extraction_mask & ord(raw_bytes[len(raw_bytes) - 1])
			buffer, buffer_size, out = FileClient.buffer_bits(extracted, buffer, buffer_size, 8)
			if not out is None:
				data.append(out)
		if buffer > 1:
			buffer <<= 8 - buffer_size
			out = buffer & 255
			data.append(out)
		return data

# Iterate through a list of numbers and return each of those
# 8 bits or less at a time
def iter_bytes(nums):
	for num in nums:
		while num:
			yield num & 255
			num >>= 8

# Find the number of digits in number n from base b.
# I could do this with log but it's slower.
def num_digits(n, b):
	step = b
	digits = 1
	while True:
		if step > n:
			return digits
		step *= b
		digits += 1

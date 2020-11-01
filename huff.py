import os, sys, heapq

class HuffmanNode:
	def __init__(self, freq, char=None, left=None, right=None):
		self.freq = freq
		self.char = char
		self.left = left
		self.right = right

	def __lt__(self, other):
		return self.freq < other.freq

	def isLeafNode(self):
		return self.left == None and self.right == None


class HuffmanEncoder:
	def __init__(self, source, dest):
		self.input_file = open(source, 'r')
		self.input_file.seek(0, 2)
		self.EOF = self.input_file.tell()
		self.input_file.seek(0, 0)
		self.freqDict = {}
		self.HuffmanCodes = {}
		self.allChar = []
		self.output_file = open(dest, 'wb')
		self.root = None

	def countCharFreq(self):
		advance = True
		while advance:
			char = self.input_file.read(1)
			self.allChar.append(char)
			if char in self.freqDict:
				self.freqDict[char] += 1
			else:
				self.freqDict[char] = 1

			if(self.input_file.tell() == self.EOF):
				advance = False

	def buildHuffmanTree(self):
		nodes = []
		for char in self.freqDict:
			nodes.append(HuffmanNode(self.freqDict[char], char))

		heapq.heapify(nodes)

		while(len(nodes) > 1):
			left_child = heapq.heappop(nodes)
			right_child = heapq.heappop(nodes)
			blank_parent_node = HuffmanNode(left_child.freq + right_child.freq, left=left_child, right=right_child)
			heapq.heappush(nodes, blank_parent_node)

		return heapq.heappop(nodes)

	def inOrderHuffmanCode(self, rootNode, binary_code_str=''):
		if rootNode != None:
			self.inOrderHuffmanCode(rootNode.left, binary_code_str + '0')
			if rootNode.isLeafNode():
				self.HuffmanCodes[rootNode.char] = binary_code_str
			self.inOrderHuffmanCode(rootNode.right, binary_code_str + '1')

	def encodeFile(self):
		def toBytes(encoded_string):
			byte = bytearray()
			for i in range(0, len(encoded_string), 8):
				byte.append(int(encoded_string[i:i+8], 2))
			return bytes(byte)

		def encodeHuffmanTree(node, encoded_tree):
			if node.char is not None:
				encoded_tree += "1"
				encoded_tree += "{0:08b}".format(ord(node.char))
			else:
				encoded_tree += "0"
				encoded_tree = encodeHuffmanTree(node.left, encoded_tree)
				encoded_tree = encodeHuffmanTree(node.right, encoded_tree)
			return encoded_tree

		def padEncodedString(self, encoded_string):
			encoded_tree = encodeHuffmanTree(self.root, "")
			padding = 8 - (len(encoded_string) + len(encoded_tree)) % 8
			for i in range(padding):
				encoded_string += "0"

			padded_info = "{0:08b}".format(padding)
			encoded_string = encoded_tree + padded_info + encoded_string
			return encoded_string

		encoded_string  = ''
		for char in self.allChar:
			encoded_string += self.HuffmanCodes[char]

		self.output_file.write(toBytes(padEncodedString(self, encoded_string)))
		self.output_file.close()



class HuffmanDecoder():
	def __init__(self, source, dest):
		self.input_file = open(source, 'rb')
		self.output_file = open(dest, 'w')

	def decodeFile(self):
		def decodeHuffmanTree(binary_string):
			bit = binary_string[0]
			del binary_string[0]

			if bit == "1":
				char = ""
				for x in range(8):
					char += binary_string[0]
					del binary_string[0]

				return HuffmanNode(freq=None, char=chr(int(char, 2)))
			return HuffmanNode(freq=None, left=decodeHuffmanTree(binary_string), right=decodeHuffmanTree(binary_string))
		
		def removePadding(binary_string):
			padding_info = binary_string[:8]
			padding_len = int("".join(padding_info), 2)

			padding_info_removed = binary_string[8:]
			padding_removed_string = padding_info_removed[:-1*padding_len]
	
			return padding_removed_string

		def decodeText(encoded_string, rootNode):
			curr_node = rootNode
			decoded_string = ''

			for char in encoded_string:
				curr_node = curr_node.left if char == "0" else curr_node.right

				if curr_node.char is not None:
					decoded_string += curr_node.char
					curr_node = rootNode

			return decoded_string

		binary_string = ''
		byte = self.input_file.read(1)
		while(len(byte) > 0):
			byte = ord(byte)
			bits = bin(byte)[2:].rjust(8, '0')
			binary_string += bits
			byte = self.input_file.read(1)

		binary_string = list(binary_string)
		rootNode = decodeHuffmanTree(binary_string)
		encoded_string = removePadding(binary_string)
		decoded_string = decodeText(encoded_string, rootNode)
		self.output_file.write(decoded_string)



def printCompressionRate(input_path, output_path):
	input_file_size = os.path.getsize(input_path)
	output_file_size = os.path.getsize(output_path)
	compression_rate = round((input_file_size - output_file_size)/input_file_size * 100)
	print("Compression Successful. Details:")
	print("Original File Size: ", input_file_size)
	print("Compressed File Size: ", output_file_size)
	print("New File Is", compression_rate, "% Of The Original File.\n")

def runEncoder(encoder, input_path, output_path):
	encoder.countCharFreq()
	headNode = encoder.buildHuffmanTree()
	encoder.inOrderHuffmanCode(headNode)
	encoder.root = headNode
	encoder.encodeFile()
	printCompressionRate(input_path, output_path)

def main():
	mode = sys.argv[1]
	input_path = sys.argv[2]
	if mode == 'compress':
		if os.path.isfile(input_path):
			output_path = input_path.split('.')[0] + 'Compressed.bin'
			encoder = HuffmanEncoder(input_path, output_path)
			runEncoder(encoder, input_path, output_path)
		else:
			files = [file for file in os.listdir(input_path) if file.endswith(".txt")]
			for f in files:
				output_path = input_path + '/' + f.split('.')[0] + 'Compressed.bin'
				encoder = HuffmanEncoder(input_path + '/' + f, output_path)
				runEncoder(encoder, input_path + '/' + f, output_path)
	elif mode == 'decompress':
		if os.path.isfile(input_path):
			output_path = input_path.split('.')[0][:-1*len('Compressed')] + 'Decompressed.txt'
			decoder = HuffmanDecoder(input_path, output_path)
			decoder.decodeFile()
			print("Decompression Successful.")
		else:
			files = [file for file in os.listdir(input_path) if file.endswith(".bin")]
			for f in files:
				output_path = input_path + '/' + f.split('.')[0][:-1*len('Compressed')] + 'Decompressed.txt'
				decoder = HuffmanDecoder(input_path + '/' + f, output_path)
				decoder.decodeFile()
				print("Decompression Successful.")
	else:
		print('Invalid Mode.')


if __name__ == "__main__":
	main()



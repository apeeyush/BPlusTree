import sys
import bisect
import os.path
import time
import numpy

class Node:
	def __init__(self, filename=None):
		if filename:
			self.read_data_from_file(filename)

	def read_data_from_file(self, filename):
		global filecounter
		global disk_counter
		disk_counter += 1
		filepath = 'data/'+filename
		lines = [line.strip() for line in open(filepath)]
		self.keys = [float(key) for key in lines[0].split(',')]
		self.children = [child.strip() for child in lines[1].split(',')]
		if lines[2] == 'True':
			self.is_leaf = True
		else:
			self.is_leaf = False
		self.filename = filename
		if self.is_leaf and len(lines) >= 4:
			self.next = lines[3].strip()
		else:
			self.next = None

	def write_data_to_file(self, filename):
		global disk_counter
		disk_counter += 1
		filepath = 'data/' + filename
		with open(filepath, 'w') as f:
			f.write(str(self.keys).strip('[]').replace("'",""))
			f.write('\n')
			f.write(str(self.children).strip('[]').replace("'",""))
			f.write('\n')
			f.write(str(self.is_leaf))
			f.write('\n')
			if self.is_leaf and self.next:
				f.write(str(self.next))
				f.write('\n')

	def printContent(self):
		print self.keys
		print self.children
		print self.is_leaf
		print self.filename
		if self.is_leaf:
			print self.next
		else:
			print 'None'

	def updateNode(self):
		self.write_data_to_file(self.filename)

	def splitNode(self):
		global filecounter
		newNode = Node()
		newNode.filename = str(filecounter)
		filecounter = filecounter+1
		if self.is_leaf:
			newNode.is_leaf = True
			mid = len(self.keys)/2
			midKey = self.keys[mid]
			# Update sibling parameters
			newNode.keys = self.keys[mid:]
			newNode.children = self.children[mid:]
			# Update node parameters
			self.keys = self.keys[:mid]
			self.children = self.children[:mid]
			# Update next node pointers
			newNode.next = self.next
			self.next = newNode.filename
		else:
			newNode.is_leaf = False
			mid = len(self.keys)/2
			midKey = self.keys[mid]
			# Update sibling parameters
			newNode.keys = self.keys[mid+1:]
			newNode.children = self.children[mid+1:]
			# Update node parameters
			self.keys = self.keys[:mid]
			self.children = self.children[:mid + 1]
		self.updateNode()
		newNode.updateNode()
		return midKey, newNode

class BPlusTree:
	def __init__(self, factor, rootfile=-1):
		self.factor = factor
		if rootfile == -1:
			self.root = Node()
			# Initialize root
			global filecounter
			self.root.is_leaf = True
			self.root.keys = []
			self.root.children = []
			self.root.next = None
			self.root.filename = str(filecounter)
			filecounter += 1
			self.root.updateNode()
		else:
			self.root = Node(rootfile)

	def search(self, key):
		return self.tree_search(key, self.root)

	def tree_search(self, key, node):
		if node.is_leaf:
			return node
		else:
			if key < node.keys[0]:
				return self.tree_search(key, Node(node.children[0]))
			for i in range(len(node.keys)-1):
				if key>=node.keys[i] and key<node.keys[i+1]:
					return self.tree_search(key, Node(node.children[i+1]))
			if key >= node.keys[-1]:
				return self.tree_search(key, Node(node.children[-1]))

	def tree_search_for_query(self, key, node):
		if node.is_leaf:
			return node
		else:
			if key <= node.keys[0]:
				return self.tree_search_for_query(key, Node(node.children[0]))
			for i in range(len(node.keys)-1):
				if key>node.keys[i] and key<=node.keys[i+1]:
					return self.tree_search_for_query(key, Node(node.children[i+1]))
			if key > node.keys[-1]:
				return self.tree_search_for_query(key, Node(node.children[-1]))

	def point_query(self, key):
		all_keys = []
		all_values = []
		start_leaf = self.tree_search_for_query(key, self.root)
		keys, values, next_node = self.get_data_in_key_range(key, key, start_leaf)
		all_keys += keys
		all_values += values
		while next_node:
			keys, values, next_node = self.get_data_in_key_range(key, key, Node(next_node.filename))
			all_keys += keys
			all_values += values
		return all_keys, all_values

	def range_query(self, keyMin, keyMax):
		all_keys = []
		all_values = []
		start_leaf = self.tree_search_for_query(keyMin, self.root)
		keys, values, next_node = self.get_data_in_key_range(keyMin, keyMax, start_leaf)
		all_keys += keys
		all_values += values
		while next_node:
			keys, values, next_node = self.get_data_in_key_range(keyMin, keyMax, Node(next_node.filename))
			all_keys += keys
			all_values += values
		return all_keys, all_values

	def get_data_in_key_range(self, keyMin, keyMax, node):
		keys = []
		values = []
		for i in range(len(node.keys)):
			key = node.keys[i]
			if keyMin <= key and key <= keyMax:
				keys.append(key)
				values.append(self.read_data_file(node.children[i]))
		if node.keys[-1] > keyMax:
			next_node = None
		else:
			if node.next:
				next_node = Node(node.next)
			else:
				next_node = None
		return keys, values, next_node

	def insert(self, key, value):
		ans, newFilename =  self.tree_insert(key, value, self.root)
		if ans:
			global filecounter
			newRoot = Node()
			newRoot.is_leaf = False
			newRoot.filename = str(filecounter)
			filecounter += 1
			newRoot.keys = [ans]
			newRoot.children = [self.root.filename, newFilename]
			newRoot.updateNode()
			self.root = newRoot

	def tree_insert(self, key, value, node):
		if node.is_leaf:
			index = bisect.bisect(node.keys, key)
			node.keys[index:index] = [key]
			filename = self.create_data_file(value)
			node.children[index:index] = [filename]
			node.updateNode()
			if len(node.keys) <= self.factor-1:
				return None, None
			else:
				midKey, newNode = node.splitNode()
				return midKey, newNode.filename
		else:
			if key < node.keys[0]:
				ans, newFilename = self.tree_insert(key, value, Node(node.children[0]))
			for i in range(len(node.keys)-1):
				if key>=node.keys[i] and key<node.keys[i+1]:
					ans, newFilename = self.tree_insert(key, value, Node(node.children[i+1]))
			if key >= node.keys[-1]:
				ans, newFilename = self.tree_insert(key, value, Node(node.children[-1]))
		if ans:
			index = bisect.bisect(node.keys, ans)
			node.keys[index:index] = [ans]
			node.children[index+1:index+1] = [newFilename]
			if len(node.keys) <= self.factor-1:
				node.updateNode()
				return None, None
			else:
				midKey, newNode = node.splitNode()
				return midKey, newNode.filename
		else:
			return None, None

	def create_data_file(self, value):
		global filecounter
		global disk_counter
		disk_counter += 1
		filename = str(filecounter)
		filepath = 'data/'+filename
		with open(filepath, 'w') as f:
			f.write(str(value))
		filecounter += 1
		return filename

	def read_data_file(self, filename):
		global disk_counter
		disk_counter += 1
		filepath = 'data/'+filename
		lines = [line.strip() for line in open(filepath)]
		return lines[0].strip()

def save_tree(root, filecounter):
	filepath = '.bplustree'
	with open(filepath, 'w') as f:
		f.write(root)
		f.write('\n')
		f.write(str(filecounter))
		f.write('\n')

def write_stats():
	filepath = 'stats.txt'
	global insert_time
	global search_time
	global range_time
	insert_time = numpy.array(insert_time)
	search_time = numpy.array(search_time)
	range_time  = numpy.array(range_time)
	with open(filepath, 'w') as f:
		if len(insert_time)>0:
			f.write('Insert time statistics (In seconds)..\n')
			f.write('Min : '+str(numpy.amin(insert_time))+'\n')
			f.write('Max : '+str(numpy.amax(insert_time))+'\n')
			f.write('Mean: '+str(numpy.mean(insert_time))+'\n')
			f.write('STD : '+str(numpy.std(insert_time))+'\n')

			f.write('Insert disk statistics..\n')
			f.write('Min : '+str(numpy.amin(insert_disk))+'\n')
			f.write('Max : '+str(numpy.amax(insert_disk))+'\n')
			f.write('Mean: '+str(numpy.mean(insert_disk))+'\n')
			f.write('STD : '+str(numpy.std(insert_disk))+'\n')
			f.write('\n')
		if len(search_time)>0:
			f.write('Point time statistics (In seconds)..\n')
			f.write('Min : '+str(numpy.amin(search_time))+'\n')
			f.write('Max : '+str(numpy.amax(search_time))+'\n')
			f.write('Mean: '+str(numpy.mean(search_time))+'\n')
			f.write('STD : '+str(numpy.std(search_time))+'\n')

			f.write('Point disk statistics..\n')
			f.write('Min : '+str(numpy.amin(search_disk))+'\n')
			f.write('Max : '+str(numpy.amax(search_disk))+'\n')
			f.write('Mean: '+str(numpy.mean(search_disk))+'\n')
			f.write('STD : '+str(numpy.std(search_disk))+'\n')
			f.write('\n')
		if len(range_time)>0:
			f.write('Range time statistics (In seconds)..\n')
			f.write('Min : '+str(numpy.amin(range_time))+'\n')
			f.write('Max : '+str(numpy.amax(range_time))+'\n')
			f.write('Mean: '+str(numpy.mean(range_time))+'\n')
			f.write('STD : '+str(numpy.std(range_time))+'\n')

			f.write('Range disk statistics..\n')
			f.write('Min : '+str(numpy.amin(range_disk))+'\n')
			f.write('Max : '+str(numpy.amax(range_disk))+'\n')
			f.write('Mean: '+str(numpy.mean(range_disk))+'\n')
			f.write('STD : '+str(numpy.std(range_disk))+'\n')
			f.write('\n')

if __name__ == '__main__':
	# Initialize variables
	filecounter = 0 		# Used to keep track of filename
	disk_counter = 0 		# Used to count disk access
	start_time = 0 			# Used to store start time
	end_time = 0 			# Used to store end time
	insert_time = []
	search_time = []
	range_time = []
	insert_disk = []
	search_disk = []
	range_disk = []
	# Load Configuration
	configs = [line.strip() for line in open('bplustree.config')]
	max_num_keys = int(configs[0].strip())
	factor = max_num_keys-1

	# Do not initialize the tree.. Load from .bplustree
	if os.path.isfile('.bplustree'):
		filepath = '.bplustree'
		lines = [line.strip() for line in open(filepath)]
		root = lines[0].strip()
		tree = BPlusTree(factor, root)
		filecounter = int(lines[1].strip())
	# Initialize the tree
	else:
		tree = BPlusTree(factor)

	# Perform insert operations
	if sys.argv[1] == 'insert':
		print 'Inserting Data'
		if len(sys.argv) >= 3:
			filepath = sys.argv[2]
		else:
			filepath = 'assgn2_bplus_data.txt'
		lines = [line.strip() for line in open(filepath)]
		for line in lines:
			line = line.split()
			key = float(line[0].strip())
			value = line[1].strip()
			start_time = time.clock()
			disk_counter = 0
			tree.insert(key, value)
			end_time = time.clock()
			insert_time.append(end_time-start_time)
			insert_disk.append(disk_counter)
		print 'Insertions successfully completed'

	# Perform query operations
	if sys.argv[1] == 'query':
		print 'Running queries'
		if len(sys.argv) >= 3:
			filepath = sys.argv[2]
		else:
			filepath = 'querysample.txt'
		# Query
		lines = [line.strip() for line in open(filepath)]
		for line in lines:
			line = line.split()
			operation = int(line[0].strip())
			# Insertion
			if operation == 0:
				key = float(line[1].strip())
				value = line[2].strip()
				start_time = time.clock()
				disk_counter = 0
				tree.insert(key, value)
				end_time = time.clock()
				insert_time.append(end_time-start_time)
				insert_disk.append(disk_counter)
				print 'insert:', key, value
			# Point Query
			elif operation == 1:
				key = float(line[1].strip())
				start_time = time.clock()
				disk_counter = 0
				keys, values = tree.point_query(key)
				end_time = time.clock()
				search_time.append(end_time-start_time)
				search_disk.append(disk_counter)
				print 'search:', key
				if len(values) > 0:
					print values
				else:
					print 'Not Found'
			# Range Query
			elif operation == 2:
				center = float(line[1].strip())
				qrange = float(line[2].strip())
				keyMin = center-qrange
				keyMax = center+qrange
				print 'range:'
				eps = 0.00000001
				start_time = time.clock()
				disk_counter = 0
				keys, values = tree.range_query(keyMin-eps, keyMax+eps)
				end_time = time.clock()
				range_time.append(end_time-start_time)
				range_disk.append(disk_counter)
				if len(values) > 0:
					zipped = zip(keys, values)
					print zipped
				else:
					print 'Not Found'

	# Save tree configuration
	write_stats()
	save_tree(tree.root.filename, filecounter)

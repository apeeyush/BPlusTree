import bisect

class Node:
	# def __init__(self, keys = [], children = [], is_leaf = False):
	# 	self.keys = keys
	# 	self.children = children
	# 	self.is_leaf = is_leaf
	# 	self.filename = None
	def __init__(self, filename=None):
		if filename:
			self.read_data_from_file(filename)

	def read_data_from_file(self, filename):
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
	def __init__(self, factor):
		self.factor = factor
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
				return self.tree_search(key, Node(node.children[0]))
			for i in range(len(node.keys)-1):
				if key>node.keys[i] and key<=node.keys[i+1]:
					return self.tree_search(key, Node(node.children[i+1]))
			if key > node.keys[-1]:
				return self.tree_search(key, Node(node.children[-1]))

	def point_query(self, key):
		all_values = []
		start_leaf = self.tree_search_for_query(key, self.root)
		values, next_node = self.get_values_in_key_range(key, key, start_leaf)
		all_values += values
		while next_node:
			values, next_node = self.get_values_in_key_range(key, key, Node(next_node.filename))
			all_values += values
		return all_values

	def range_query(self, keyMin, keyMax):
		all_values = []
		start_leaf = self.tree_search_for_query(keyMin, self.root)
		values, next_node = self.get_values_in_key_range(keyMin, keyMax, start_leaf)
		all_values += values
		while next_node:
			values, next_node = self.get_values_in_key_range(keyMin, keyMax, Node(next_node.filename))
			all_values += values
		return all_values

	def get_values_in_key_range(self, keyMin, keyMax, node):
		values = []
		for i in range(len(node.keys)):
			key = node.keys[i]
			if keyMin <= key and key <= keyMax:
				values.append(self.read_data_file(node.children[i]))
		if node.keys[-1] > keyMax:
			next_node = None
		else:
			if node.next:
				next_node = Node(node.next)
			else:
				next_node = None
		return values, next_node

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
		# bucket = self.search(key)
		# index = bisect.bisect(bucket.keys, key)
		# bucket.keys[index:index] = [key]
		# filename = self.create_data_file(value)
		# bucket.children[index:index] = [filename]
		# bucket.updateNode()
		# if len(bucket.keys) <= self.factor-1:
		# 	return None
		# else:
		# 	midKey, newNode = bucket.splitNode()
		# 	return midKey

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
			node.keys[index:index] = [key]
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
		filename = str(filecounter)
		filepath = 'data/'+filename
		with open(filepath, 'w') as f:
			f.write(str(value))
		filecounter += 1
		return filename

	def read_data_file(self, filename):
		filepath = 'data/'+filename
		lines = [line.strip() for line in open(filepath)]
		return lines[0].strip()

if __name__ == '__main__':
	filecounter=11
	tree = BPlusTree(4)
	tree.insert(0.31,111)
	tree.insert(0.33,113)
	tree.insert(0.33,115)
	tree.insert(0.39,119)
	tree.insert(0.33,119)
	tree.insert(0.31,111)
	tree.insert(0.33,113)
	tree.insert(0.33,115)
	tree.insert(0.39,119)
	tree.insert(0.33,119)
	tree.insert(0.31,111)
	tree.insert(0.33,113)
	tree.insert(0.33,115)
	tree.insert(0.39,119)
	tree.insert(0.33,119)
	tree.insert(0.31,111)
	tree.insert(0.33,113)
	tree.insert(0.33,115)
	tree.insert(0.39,119)
	tree.insert(0.33,119)
	print tree.range_query(0.31,0.39)
	print tree.root.filename

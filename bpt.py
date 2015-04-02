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
		print self.next

	def updateNode(self):
		self.write_data_to_file(self.filename)

	def splitNode(self):
		global filecounter
		newNode = Node()
		if self.is_leaf:
			mid = len(self.keys)/2
			midKey = self.keys[mid]
			# Update sibling parameters
			newNode.keys = self.keys[mid:]
			newNode.children = self.children[mid:]
			# Update node parameters
			self.keys = self.keys[:mid]
			self.children = self.children[:mid]
		else:
			mid = len(self.keys)/2
			midKey = self.keys[mid]
			# Update sibling parameters
			newNode.keys = self.keys[mid+1:]
			newNode.children = self.children[mid+1:]
			# Update node parameters
			self.keys = self.keys[:mid]
			self.children = self.children[:mid + 1]
		newNode.is_leaf = True
		newNode.filename = str(filecounter)
		newNode.next = self.next
		self.next = newNode.filename
		filecounter = filecounter+1
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

	def add_key(self, key):
		pass

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
			print index
			node.keys[index:index] = [key]
			node.children[index+1:index+1] = [newFilename]
			node.printContent()
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
		filename = 'data/'+str(filecounter)
		with open(filename, 'w') as f:
			f.write(str(value))
		filecounter += 1
		return filename

if __name__ == '__main__':
	filecounter=11
	tree = BPlusTree(4)
	tree.insert(0.33,111)
	tree.insert(0.33,111)
	tree.insert(0.33,111)
	tree.insert(0.33,111)

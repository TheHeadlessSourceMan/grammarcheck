class DocumentChecker(object):
	"""
	This class represents a full-doc grammar/spelling checker.
	
	In general, sentence checkers are better and faster, but not always possible.
	"""
	
	def __init__(self,name):
		self.name=name
		
	def checkDocument(self,doc):
		"""
		Sub classes must implement this
	
		returns [DocProblem]
		"""
		raise NotImplementedError()
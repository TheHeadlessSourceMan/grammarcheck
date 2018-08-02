class SentenceChecker(object):
	"""
	This class represents a sentence-by-sentence grammar/spelling checker.
	"""
	
	def __init__(self,name):
		self.name=name
		
	def checkSentence(self,sentence):
		"""
		Sub classes must implement this
		
		returns [DocProblem]
		"""
		raise NotImplementedError()
	
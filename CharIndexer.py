class CharIndexer:
	"""
	find the character index within a file
	"""
	def __init__(self,doc):
		self.lines=[] # (charStart,charEnd)
		charEnd=-1
		for line in doc.split('\n'):
			charStart=charEnd+1
			charEnd=charStart+len(line)
			self.lines.append((charStart,charEnd))
			
	
	def charIndexToLineChar(self,charIndex,zeroBasedIndexing=False):
		"""
		convert an absolute character index to a line number + character offset
		
		if zeroBasedIndexing=True, then the first line,character is 0,0
			otherwise, it is 1,1
		
		returns (line,char)
		
		If the line is not in the given file, return None
		"""
		for lineNo in range(len(self.lines)):
			if charIndex<=self.lines[lineNo][1]:
				if zeroBasedIndexing:
					return (lineNo,charIndex-self.lines[lineNo][0])
				else:
					return (lineNo+1,charIndex-self.lines[lineNo][0]+1)
		return None
		
	def charIndexToFilenameIndicator(self,charIndex,zeroBasedIndexing=False,charOffsetSep=',',includeCharOffset=True):
		"""
		if zeroBasedIndexing=True, then the first line,character is 0,0
			otherwise, it is 1,1
		
		return the charIndex to an :line,char indicator to append to a filename, 
		such as foo.txt:21,4
		"""
		idx=self.charIndexToLineChar(charIndex,zeroBasedIndexing)
		if includeCharOffset:
			return ':'+str(idx[0])+charOffsetSep+str(str(idx[1]))
		return ':'+str(idx[0])
		
		
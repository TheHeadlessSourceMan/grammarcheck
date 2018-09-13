"""
This does a quick grammar fix of all the quotes in a text
"""
from docStructure import re
from grammarcheck import *

QUOTE_REGEX=re.compile(r"""\n\s*?\n+""")

class QuoteFixer(DocumentChecker):
	"""
	This does a quick grammar fix of all the quotes in a text
	"""
	def __init__(self):
		DocumentChecker.__init__(self,'Quote_Fixer')
		self.severity=0.80;
		self.certainty=0.80;

	def checkDocument(self,doc,idx=0):
		"""
		:param doc: the document to check
		:param idx: start location for the check
		
		:return: [DocProblem]
		"""
		problems=[]
		endIdx=idx-1
		while True:
			startIdx=doc.find('"',endIdx+1)
			if startIdx<0:
				break
			endIdx=doc.find('"',startIdx+1)
			if endIdx<0:
				break
			# rule to fix multiline quotes
			# TODO: could be better?  For now, simply plop a quote on the beginning of the next line\
			mult=QUOTE_REGEX.search(doc,startIdx)
			if mult!=None:
				if endIdx>mult.start():
					#doc=doc[0:mult.start()+2]+'"'+doc[mult.start()+2:]  # this is what the replacement would be like
					problems.append(DocProblem(
						'fix multiline quotes',
						doc[mult.start()+2].word,
						self.severity,self.certainty,
						start_idx=mult.start()+2,
						end_idx=mult.start()+2,
						name='',
						replacements=['"'],
						fromChecker=self,
						doc=doc))
					#continue
			# rule to remove extra space between quote and comma: "abc" , said she
			if re.match('["]\startIdx+,',doc[endIdx:]):
				while doc[endIdx+1]==' ':
					#doc=doc[0:endIdx+1]+doc[endIdx+2:] # this is what the replacement would be like
					problems.append(DocProblem(
						'remove extra space between quote and comma: "abc" , said she',
						doc[endIdx+2].word,
						self.severity,self.certainty,
						start_idx=endIdx+1,
						end_idx=endIdx+2,
						name='',
						replacements=[''],
						fromChecker=self,
						doc=doc))
			# rule to remove comma from: "abc!", said she.
			if doc[endIdx-1] in ['!','.','?']:
				if len(doc)>endIdx+1 and doc[endIdx+1]==',':
					#doc=doc[0:endIdx+1]+doc[endIdx+2:]  # this is what the replacement would be like
					problems.append(DocProblem(
						'remove unneeded comma from: "abc!", said she.',
						doc[endIdx+2].word,
						self.severity,self.certainty,
						start_idx=endIdx+1,
						end_idx=endIdx+2,
						name='',
						replacements=[''],
						fromChecker=self,
						doc=doc))
			# rule to add comma to: "abc" said she.
			else:
				if re.match('\startIdx*[a-z0-9]',doc[endIdx+1:]):
					#doc=doc[0:endIdx+1]+','+doc[endIdx+1:] # this is what the replacement would be like
					problems.append(DocProblem(
						'add comma to quote like: "abc" said she.',
						doc[endIdx+1].word,
						self.severity,self.certainty,
						start_idx=endIdx+1,
						end_idx=endIdx+1,
						name='',
						replacements=[','],
						fromChecker=self,
						doc=doc))
			# rule to add space between major and minor quotes like "'incredible'", she mimicked
			if doc[startIdx+1]=="'":
				#doc=doc[0:startIdx+1]+' '+doc[startIdx+1:] # this is what the replacement would be like
				problems.append(DocProblem(
					'add space between major and minor quotes like "\'incredible\'", she mimicked',
					doc[startIdx+1].word,
					self.severity,self.certainty,
					start_idx=startIdx+1,
					end_idx=startIdx+1,
					name='',
					replacements=[' '],
					fromChecker=self,
					doc=doc))
				endIdx=endIdx+1
			if doc[endIdx-1]=="'":
				#doc=doc[0:endIdx]+' '+doc[endIdx:]  # this is what the replacement would be like
				problems.append(DocProblem(
					'add space between major and minor quotes like "\'incredible\'", she mimicked',
					doc[endIdx].word,
					self.severity,self.certainty,
					start_idx=endIdx,
					end_idx=endIdx,
					name='',
					replacements=[' '],
					fromChecker=self,
					doc=doc))
				endIdx=endIdx+1
		return problems
		
		
def QQF(text,idx=0):
	"""
	Utility to automatically try to fix all quotes in a file.
	
	The checker above was derived from this tool.
	"""
	e=idx-1
	while True:
		s=text.find('"',e+1)
		if s<0:
			break
		e=text.find('"',s+1)
		if e<0:
			break
		# rule to fix multiline quotes
		# TODO: could be better?  For now, simply plop a quote on the beginning of the next line\
		mult=QUOTE_REGEX.search(text,s)
		if mult!=None:
			if e>mult.start():
				text=text[0:mult.start()+2]+'"'+text[mult.start()+2:]
				#continue
		# rule to remove extra space between quote and comma: "abc" , said she
		if re.match('["]\s+,',text[e:]):
			while text[e+1]==' ':
				text=text[0:e+1]+text[e+2:]
		# rule to remove comma from: "abc!", said she.
		if text[e-1] in ['!','.','?']:
			if len(text)>e+1 and text[e+1]==',':
				text=text[0:e+1]+text[e+2:]
		# rule to add comma to: "abc" said she.
		else:
			if re.match('\s*[a-z0-9]',text[e+1:]):
				text=text[0:e+1]+','+text[e+1:]
		# rule to add space between major and minor quotes like "'incredible'", she mimicked
		if text[s+1]=="'":
			text=text[0:s+1]+' '+text[s+1:]
			e=e+1
		if text[e-1]=="'":
			text=text[0:e]+' '+text[e:]
			e=e+1
	return text
	
	
Tests=[# (test,result) 
	('"abc" , said she.','"abc", said she.'),
	('"abc!", said she.','"abc!" said she.'),
	('"abc" said she.','"abc", said she.'),
	('\"First line\n\nsecond line\"','\"First line\n\n\"second line\"'),
	('"\'Incredible\', indeed!"','" \'Incredible\', indeed!"'),
	('"Indeed \'Incredible\'"','"Indeed \'Incredible\' "')
]

def Test():
	for test in range(len(Tests)):
		result=QQF(Tests[test][0])
		if result==Tests[test][1]:
			print 'Test',test,'= PASSED'
		else:
			print 'Test',test,'= FAILED'
			print 'Given:\n\t',Tests[test][0]
			print 'Expected:\n\t',Tests[test][1]
			print 'Actual:\n\t',result
			

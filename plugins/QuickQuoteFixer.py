"""
This does a quick grammar fix of all the quotes in a text
"""
from docStructure import re
from grammarcheck import *

class QuoteFixer(DocumentChecker):
	def __init__(self):
		DocumentChecker.__init__(self,'Quote_Fixer')

	def checkDocument(self,doc):
		# TODO: QQF needs to be rewritten to spit out DocumentProblem objects
		return []
		
def QQF(text,idx=0):
	e=idx-1
	regex=r"""\n\s*?\n+"""
	regex=re.compile(regex)
	while True:
		s=text.find('"',e+1)
		if s<0:
			break
		e=text.find('"',s+1)
		if e<0:
			break
		# rule to fix multiline quotes
		# TODO: could be better?  For now, simply plop a quote on the beginning of the next line\
		mult=regex.search(text,s)
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
			

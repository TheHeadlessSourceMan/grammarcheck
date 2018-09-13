#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program will find abbreviations without proper periods
"""
from grammarcheck import *
from docStructure import *
from DocProblem import *


ABBR=['abbr',
	#'N.','S.','E.','W.',
	'Mrs.','Mr.','Ms.','Messrs.','Mmes.',
	'Prof.','Dr.','Drs.','Gen.','Lt.','Rep.','Sen.','Rev.','Hon.'
	'St.','Blvd.','Ln.',
	'Sr.','Jr.',
	#'Ph.D.','M.D.','B.A.','B.S.','M.A.','M.S.','M.B.A.','D.D.S.', # optional
	'U.K.','U.S. Army','U.S. Navy','U.S. Air Force','U.S. government','U.S. Post Office','U.S. military','U.S. Coast Guard',
	#'B.C.','A.D.','A.M.','P.M.', # I just don't like the way this looks
	'etc.','i.e.','e.g.','et al.',
]


class AbbreviationFinder(DocumentChecker):
	"""
	Find abbreviations that are not formatted correctly.
	"""
	
	REGEX=None
	
	def __init__(self):
		DocumentChecker.__init__(self,'Abbreviation_finder')
		if self.REGEX==None:
			regexes=[]
			split=r"""[,;:!?\-()\"\s'\n]+"""
			innerSplit=r"""[\s]+"""
			for i in range(len(ABBR)-1):
				abb=ABBR[i].replace('.','\.?')
				regexes.append('(?:'+abb+')')
			regex=split+'('+('|'.join(regexes))+')'+split
			#print regex
			#print
			self.REGEX=re.compile(regex,re.IGNORECASE|re.DOTALL)

	def checkSentence(self,doc):
		"""
		:param doc: the document object to check for errors
		:return: [DocProblem]
		"""
		ret=[]
		for match in self.REGEX.finditer(doc.text):
			if match.group(1) not in ABBR: # if its not exactly how it should be
				dp=DocProblem(description='abbreviation not formatted correctly',
					atWord=None,severity=0.85,certainty=0.9,
					start_idx=match.start(1),end_idx=match.end(1),
					name='',replacements=[],fromChecker=self,doc=doc)
				ret.append(dp)
		return ret
	

if __name__ == '__main__':
	import sys
	# Use the Psyco python accelerator if available
	# See:
	# 	http://psyco.sourceforge.net
	try:
		import psyco
		psyco.full() # accelerate this program
	except ImportError:
		pass
	printhelp=False
	if len(sys.argv)<2:
		printhelp=True
	else:
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg in ['-h','--help']:
					printhelp=True
				else:
					print 'ERR: unknown argument "'+arg+'"'
			else:
				print 'In',arg,':'
				f=open(arg,'r')
				doc=f.read()
				f.close()
				af=AbbreviationFinder()
				bad=checkSentence(doc)
				idxr=CharIndexer(doc)
				for b in bad:
					idx=idxr.charIndexToFilenameIndicator(b[0])
					idx2=idxr.charIndexToFilenameIndicator(b[1])
					idx2=idx2.replace(':','-')
					print arg+idx+idx2+'\t'+b[2]
				print '['+str(len(bad))+' items total]'
				print 'including:'
				stuff={}
				for b in bad:
					if not stuff.has_key(b[2]):
						stuff[b[2]]=b
						print '\t'+b[2]
	if printhelp:
		print 'Usage:'
		print '  abbreviations.py [options] file'
		print 'Options:'
		print '   NONE'

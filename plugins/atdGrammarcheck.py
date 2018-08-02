#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is glue to use the After The Deadline grammar checker
"""
from grammarcheck import *
import AtdGrammarcheck


class AtdSentenceChecker(SentenceChecker):
	
	ATD=None
	
	def __init__(self):
		SentenceChecker.__init__(self,'Bad_Content_Finder')
		if self.ATD==None:
			self.ATD=AtdGrammarcheck.GrammarCheck()

	def checkSentence(self,sentence):
		"""
		"""
		ret=[]
		for err in check(str(sentence)):
			prob=DocProblem(
				description=err.description,
				atWord=None,
				severity=0,
				certainty=0.0,
				start_idx=0,
				end_idx=0,
				name=err.type,
				replacements=err.suggestions, # in preferred order
				fromChecker=self, # who caught this problem
				doc=sentence.doc)
			ret.append(prob)
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
				bc=BadContentFinder()
				bad=bc.checkSentence(doc,True)
				idxr=CharIndexer(doc)
				for b in bad:
					idx=idxr.charIndexToFilenameIndicator(b[0])
					idx2=idxr.charIndexToFilenameIndicator(b[1])
					idx2=idx2.replace(':','-')
					print arg+idx+idx2+'\t'+b[2]
				print '['+str(len(bad))+' items total]'
	if printhelp:
		print 'Usage:'
		print '  dummy.py [options]'
		print 'Options:'
		print '   NONE'

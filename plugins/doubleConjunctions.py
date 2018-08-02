#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program will find double conjunctions such as "of of" or "a an"
which is a surprisingly common typo error
"""
from docStructure import re
from grammarcheck import *

CONJ=['a','an','the','and','but','either','then','if','else','or','of','to']
OK_CONJ=['either to','but to','and to','else to','to either','then a','then an','but either','and of','if a','if an','if the','of the','then the','either the','to a','to an','to the','and if','and the','but if','but the','or else','or the','and a','and an','but a','or a','or an','of a','of an','but an','but then','and then']

COMMON_MISTAKES=['go two','go too','get two','get too','only to','to many','two many','to far','two far','to much','two much']

class BadConjFinder(SentenceChecker):
	
	REGEX=None
	
	def __init__(self):
		SentenceChecker.__init__(self,'Bad_Conjunction_Finder')
		if self.REGEX==None:
			regexes=[]
			split=r"""[,;:.!?\-()\"\s'\n]+"""
			innerSplit=r"""[\s]+"""
			for i in range(len(CONJ)-1):
				c1=CONJ[i]
				for j in range(i+1,len(CONJ)):
					c2=CONJ[j]
					if c1+' '+c2 not in OK_CONJ:
						regexes.append('(?:'+c1+innerSplit+c2+')')
					if c1!=c2 and c2+' '+c1 not in OK_CONJ:
						regexes.append('(?:'+c2+innerSplit+c1+')')
			for ckn in COMMON_MISTAKES:
				ckn=split.join(ckn.split())
				regexes.append('(?:'+ckn+')')
			regexes.append('(?:(?P<w1>[^'+split[1:-2]+']+)'+'\s+'+'(?P=w1))')# duplicates
			regex=split+'('+('|'.join(regexes))+')'+split
			#print regex
			#print
			self.REGEX=re.compile(regex,re.IGNORECASE|re.DOTALL)

	def checkSentence(self,doc):
		"""
		takes a plain text document
		
		returns [(startIndex,endIndex,problem)]
		"""
		ret=[]
		for match in self.REGEX.finditer(str(doc)):
			ret.append((match.start(1),match.end(1),str(match.group(1))))
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
				bcf=BadConjFinder()
				bad=bcf.checkSentence(doc,True)
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

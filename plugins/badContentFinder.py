#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program will find bad content including minced oaths and derogatory terms.

This is to be run after a general language filter.  That is, it will not catch f-bombs or whatever.
It assumes you have generally decent language, but might occasionally have let an "crap" or something
slip by.
"""
from docStructure import re
from grammarcheck import *

TOKEN_BOUNDARY='["\'().!?\\-\\s,;:]+'
MINCED_OATHS=['omg','crap','darn','dang','dag nabbit','dad gum','gosh','crimany','crumbs','cripes','crikey','heck','oh flip','flipping','flippin','bloody','frick','frickin','fricking',
	'for the love of(\\s+[^\\s]+)?',
	'in the name of(\\s+[^\\s]+)?',
	#'for ([^\\s]+) sake', # TODO: this needs to be smarter.  Too many false positives otherwise.
	'for (pete[\']?[s]?) sake',
	'no (.*?ing) way',
	'oh my(\\s+[^\\s]+)?',
	'holy (\\s+[^\\s]+)',
	#'what the(\\s+[^\\s]+)?' # TODO: this needs to be smarter.  Too many false positives otherwise.
	]
RUDENESS=['jerk','yuppie','stupid','idiot','moron','loser','dummy','dumb','poop','snot','fart','shut up','butt','bum','puke','barf','poo']

class BadContentFinder(SentenceChecker):
	"""
	This program will find bad content including minced oaths and derogatory terms.

	This is to be run after a general language filter.  That is, it will not catch f-bombs or whatever.
	It assumes you have generally decent language, but might occasionally have let an "crap" or something
	slip by.
	"""
	BAD_REGEX=None
	BAD_RUDE_REGEX=None
	
	def __init__(self):
		SentenceChecker.__init__(self,'Bad_Content_Finder')
		if self.BAD_REGEX==None:
			regex1=[]
			regex2=[]
			for w in MINCED_OATHS:
				m='('+w.replace(' ','\s+')+')'
				regex1.append(m)
				regex2.append(m)
			for w in RUDENESS:
				regex2.append('('+w.replace(' ','\s+')+')')
			regex1=TOKEN_BOUNDARY+'('+('|'.join(regex1))+')'+TOKEN_BOUNDARY
			regex2=TOKEN_BOUNDARY+'('+('|'.join(regex2))+')'+TOKEN_BOUNDARY
			#print regex
			#print
			self.BAD_REGEX=re.compile(regex1,re.IGNORECASE|re.DOTALL)
			self.BAD_RUDE_REGEX=re.compile(regex2,re.IGNORECASE|re.DOTALL)

	def checkSentence(self,doc,rudeness=True):
		"""
		takes a plain text document
		
		returns [(startIndex,endIndex,problem)]
		"""
		ret=[]
		if rudeness:
			regex=self.BAD_RUDE_REGEX
		else:
			regex=self.BAD_REGEX
		for match in regex.finditer(str(doc)):
			dp=DocProblem(description='bad language',
				atWord=None,severity=0.85,certainty=0.9,
				start_idx=match.start(1),end_idx=match.end(1),
				name='',replacements=[],fromChecker=self,doc='Bad words and phrases including softcore-cursing and general rudeness.  Usually the fix is to remove if completely unnecessary.  If it does have a purpose, then better to say something less lazy and more detailed anyway.  "Holy Crap!" => "Wow!  That\'s the worst scar I\'ve ever seen!"')
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

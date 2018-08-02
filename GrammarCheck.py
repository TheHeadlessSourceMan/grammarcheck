#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A simple, pluggable, python spelling/grammar checker.  Works automatically
with marked-up stuff.
"""
import os,sys
import inspect
import docStructure
from SentenceChecker import *
from DocumentChecker import *
	
HERE=os.path.abspath(__file__).rsplit(os.sep,1)[0]
PLUGINS=HERE+os.sep+'plugins'
sys.path.append(PLUGINS)
	
	
class grammarcheck:
	"""
	A simple, pluggable, python spelling/grammar checker.  Works automatically
	with marked-up stuff.
	"""
	
	ALL_DOCUMENT_CHECKERS=None
	ALL_SENTENCE_CHECKERS=None
	ALL_WORD_CHECKERS=None
	
	def __init__(self):
		if self.ALL_DOCUMENT_CHECKERS==None or self.ALL_SENTENCE_CHECKERS==None or self.ALL_WORD_CHECKERS==None:
			self.rescanPlugins()
		self.documentCheckers=self.ALL_DOCUMENT_CHECKERS.keys()
		self.sentenceCheckers=self.ALL_SENTENCE_CHECKERS.keys()
		self.wordCheckers=self.ALL_WORD_CHECKERS.keys()
		self.minCertainty=0.0 # minimum certainty required to bother user
		self.ignore=[] # ignore these problems
	
	@classmethod
	def rescanPlugins(cls):
		cls.ALL_DOCUMENT_CHECKERS={}
		cls.ALL_SENTENCE_CHECKERS={}
		cls.ALL_WORD_CHECKERS={}
		for f in os.listdir(PLUGINS):
			if f.endswith('.py') and not f.startswith('_'):
				imp=f.rsplit('.',1)[0]
				exec('import '+imp)
				m=locals()[imp]
				for item in dir(m):
					if not item.startswith('_') and item not in ['SentenceChecker','DocumentChecker']:
						item=getattr(m,item)
						if inspect.isclass(item):
							members=dir(item)
							ob=None
							if 'checkWord' in members:
								ob=item()
								cls.ALL_WORD_CHECKERS[ob.name]=ob
							if 'checkSentence' in members:
								if ob==None:
									ob=item()
								cls.ALL_SENTENCE_CHECKERS[ob.name]=ob
							if 'checkDocument' in members:
								if ob==None:
									ob=item()
								cls.ALL_DOCUMENT_CHECKERS[ob.name]=ob
	
	@classmethod
	def listAllCheckers(cls):
		if cls.ALL_DOCUMENT_CHECKERS==None or cls.ALL_SENTENCE_CHECKERS==None or cls.ALL_WORD_CHECKERS==None:
			cls.rescanPlugins()
		print 'DOCUMENT:\n\t','\n\t'.join(cls.ALL_DOCUMENT_CHECKERS.keys())
		print 'SENTENCE:\n\t','\n\t'.join(cls.ALL_SENTENCE_CHECKERS.keys())
		print 'WORD:\n\t','\n\t'.join(cls.ALL_WORD_CHECKERS.keys())
		
	def listCheckers(self):
		print 'DOCUMENT:\n\t','\n\t'.join(self.documentCheckers)
		print 'SENTENCE:\n\t','\n\t'.join(self.sentenceCheckers)
		print 'WORD:\n\t','\n\t'.join(self.wordCheckers)
	
	def disableChecker(self,name):
		for lst in [self.documentCheckers,self.sentenceCheckers,self.wordCheckers]:
			if name in lst:
				lst.remove(name)
				
	def enableChecker(self,name):
		for all,lst in [(self.ALL_DOCUMENT_CHECKERS,self.documentCheckers),(self.ALL_SENTENCE_CHECKERS,self.sentenceCheckers),(self.ALL_WORD_CHECKERS,self.wordCheckers)]:
			if name in all:
				lst.add(name)
	
	def _docbprobs(self,doc):
		docprobs=[]
		for dc in self.documentCheckers:
			if dc not in self.sentenceCheckers and dc not in self.wordCheckers:
				dc=self.ALL_DOCUMENT_CHECKERS[dc]
				docprobs.extend(dc.checkDocument(doc))
		docprobs.sort(key=lambda dp: dp.start_idx)
		return docprobs
	
	def _sentprobs(self,sentence):
		docprobs=[]
		for sc in self.sentenceCheckers:
			if sc not in self.wordCheckers:
				sc=self.ALL_SENTENCE_CHECKERS[sc]
				docprobs.extend(sc.checkSentence(sentence))
		docprobs.sort(key=lambda dp: dp.start_idx)
		return docprobs
	
	def _allowProblem(self,problem):
		if problem.certainty<self.minCertainty:
			return False
		for i in self.ignore:
			if i==problem: # TODO: make this smarter
				return False
		return True
		
	def check(self,doc,data=None,mimeType=None):
		"""
		doc - can be:
			* a docStructure.Document derived object
			* a file name
			* a URL
			* a file-like object
			* '-' to specify stdin
			* None if data is to be passed in instead
		
		data - if filename is None, pass in a data buffer
		
		mimeType - since we may not have a filename to go off, specify the file type
		
		returns [DocProblem]
		"""
		ret=[]
		# use checkInteractive, but the (lambda) function only logs the error and returns None
		self.checkInteractive(lambda dp: ret.append(dp),doc,data,mimeType)
		return ret
	
	def checkInteractive(self,askUserFn,doc,data=None,mimeType=None):
		"""
		Checks the data, calling askUserFn(docProb) for each detected problem.  The function then
		tells us what action to take.
		
		It will always return the problems in document-order.
		
		askUserFn - takes a DocProblem object and returns replacement text or None for no change
		
		doc - can be:
			* a docStructure.Document derived object
			* a file name
			* a URL
			* a file-like object
			* '-' to specify stdin
			* None if data is to be passed in instead
		
		data - if filename is None, pass in a data buffer
		
		mimeType - since we may not have a filename to go off, specify the file type
		"""
		if not isinstance(doc,docStructure.Document):
			doc=docStructure.Document(doc)
		dp=self._docbprobs(doc)
		sentences=doc.sentences
		sentNo=0
		while sentNo<len(sentences):
			recheck=False
			sentence=sentences[sentNo]
			for sp in self._sentprobs(sentence):
				# check all document problems before this sentence problem
				while len(dp)>0 and dp[0].start_idx<=sp.start_idx:
					d=dp.pop(0)
					if not self._allowProblem(d):
						continue
					repl=askUserFn(d)
					if repl!=None:
						sentence=sentence[0:d.start_idx]+repl+sentence[d.end_idx]
						sentences[sentNo]=sentence
						doc.sentences=sentences
						recheck=d.start_idx
						break
				if recheck:
					break
				# now check this sentence problem
				if not self._allowProblem(sp):
					continue
				repl=askUserFn(sp)
				if repl!=None:
					sentence=sentence[0:sp.start_idx]+repl+sentence[sp.end_idx]
					sentences[sentNo]=sentence
					doc.sentences=sentences
					recheck=sp.start_idx
					break
			if recheck!=False:
				dp=self._docbprobs(doc,start_idx=recheck)
			else:
				sentNo+=1
		# any remaining document problems	
		while len(dp)>0:
			d=dp.pop(0)
			if not self._allowProblem(d):
				continue
			repl=askUserFn(d)
			if repl!=None:
				sentence=sentence[0:d.start_idx]+repl+sentence[d.end_idx]
				sentences[sentNo]=sentence
				doc.sentences=sentences
				recheck=d.start_idx
				break
		
	def ncCheck(self,doc,data=None,mimeType=None):
		"""
		check the grammar and ask user for changes on the console (ncurses-based ui)
		
		doc - can be:
			* a docStructure.Document derived object
			* a file name
			* a URL
			* a file-like object
			* '-' to specify stdin
			* None if data is to be passed in instead
		
		data - if filename is None, pass in a data buffer
		
		mimeType - since we may not have a filename to go off, specify the file type
		"""
		import ncCheck
		nc=ncCheck.NcCheck()
		def onProblem(prob):
			subsys=prob.name
			options=prob.replacements
			errSentence,start_idx,end_idx=prob.excerpt()
			nc.run(subsys,errSentence,start_idx,end_idx,options)
		self.checkInteractive(onProblem,doc,data,mimeType)
		
	
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
		gc=grammarcheck()
		out=sys.stdout
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--list':
					gc.listCheckers()
				elif arg[0]=='--listAll':
					gc.listAllCheckers()
				elif arg[0]=='--setOut':
					if out!=sys.stdout:
						out.close()
					if len(arg)<1 or arg=='-':
						out=sys.stdout
					else:
						out=f.open(arg,'w')
				elif arg[0]=='--check':
					if len(arg)<2:
						print 'ERR: Filename required for --check'
					else:
						print gc.check(arg[1])
				elif arg[0]=='--ncCheck':
					if len(arg)<2:
						print 'ERR: Filename required for --ncCheck'
					else:
						print gc.ncCheck(arg[1])			
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				print 'ERR: unknown argument "'+arg+'"'
	if printhelp:
		print 'Description:'
		print '  A simple, pluggable, python spelling/grammar checker.  Works automatically with marked-up stuff.'
		print 'Usage:'
		print '  Finder.py [options]'
		print 'Options:'
		print '   --list ............ list checkers in use'
		print '   --listAll ......... list all available checkers'
		print '   --setOut=doc ...... set an output document (use "-" to go to stdout)'
		print '   --ncCheck=doc ..... interactive check in the console (use "-" to check from stdin)'
		print '   --check=doc ....... check entire doc and print all problems (use "-" to check from stdin)'
#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A simple, pluggable, python spelling/grammar checker.  Works automatically
with marked-up stuff.
"""
import os,sys
import time
import inspect
import docStructure
from SentenceChecker import *
from DocumentChecker import *
from DocProblem import *
	
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
		"""
		Rescan the plugins directory and add populate 
			self.ALL_DOCUMENT_CHECKERS
			self.ALL_SENTENCE_CHECKERS
			self.ALL_WORD_CHECKERS
		"""
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
		"""
		get a list of all installed checkers
		"""
		if cls.ALL_DOCUMENT_CHECKERS==None or cls.ALL_SENTENCE_CHECKERS==None or cls.ALL_WORD_CHECKERS==None:
			cls.rescanPlugins()
		print 'DOCUMENT:\n\t','\n\t'.join(cls.ALL_DOCUMENT_CHECKERS.keys())
		print 'SENTENCE:\n\t','\n\t'.join(cls.ALL_SENTENCE_CHECKERS.keys())
		print 'WORD:\n\t','\n\t'.join(cls.ALL_WORD_CHECKERS.keys())
		
	def listCheckers(self):
		"""
		get a list of all installed checkers
		"""
		print 'DOCUMENT:\n\t','\n\t'.join(self.documentCheckers)
		print 'SENTENCE:\n\t','\n\t'.join(self.sentenceCheckers)
		print 'WORD:\n\t','\n\t'.join(self.wordCheckers)
	
	def disableChecker(self,name):
		"""
		Turn off one of the checkers.
		
		:param name: name of the checker to turn off
		"""
		for lst in [self.documentCheckers,self.sentenceCheckers,self.wordCheckers]:
			if name in lst:
				lst.remove(name)
				
	def enableChecker(self,name):
		"""
		Turn on one of the checkers.
		
		:param name: name of the checker to turn on
		"""
		for all,lst in [(self.ALL_DOCUMENT_CHECKERS,self.documentCheckers),(self.ALL_SENTENCE_CHECKERS,self.sentenceCheckers),(self.ALL_WORD_CHECKERS,self.wordCheckers)]:
			if name in all:
				lst.add(name)
	
	def _docbprobs(self,doc):
		"""
		Run the given document against all document checkers.
		"""
		docprobs=[]
		if doc!=None:
			for dc in self.documentCheckers:
				if dc not in self.sentenceCheckers and dc not in self.wordCheckers:
					print 'Starting',dc
					dc=self.ALL_DOCUMENT_CHECKERS[dc]
					docprobs.extend(dc.checkDocument(doc))
					print 'Ended',dc
			docprobs.sort(key=lambda dp: dp.start_idx)
		return docprobs
	
	def _sentprobs(self,sentence):
		"""
		Run the given sentence against all sentence checkers.
		
		:param sentence: a sentence object to check
		"""
		docprobs=[]
		if sentence==None or sentence.text==None:
			raise Exception('None type is not a valid sentence to check.')
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
		
	def check(self,doc,data=None,mimeType=None,progressFn=None,statusFn=None,processes=1):
		"""
		run the active checkers over the given document
		
		:param doc: can be:
			* a docStructure.Document derived object
			* a file name
			* a URL
			* a file-like object
			* '-' to specify stdin
			* None if data is to be passed in instead
		:param data: if filename is None, pass in a data buffer
		:param mimeType: since we may not have a filename to go off, specify the file type
		
		:return: [DocProblem]
		"""
		ret=[]
		# use checkInteractive, but the (lambda) function only logs the error and returns None
		self.checkInteractive(lambda dp: ret.append(dp),doc,data,mimeType,progressFn,statusFn,processes)
		return ret
	
	def checkInteractive(self,askUserFn,doc,data=None,mimeType=None,progressFn=None,statusFn=None,processes=1):
		"""
		Checks the data, calling askUserFn(docProb) for each detected problem.  The function then
		tells us what action to take.
		
		It will always return the problems in document-order.
		
		:param askUserFn: a callback function that takes a DocProblem object and 
			returns replacement text or None for no change
		:param doc: can be:
			* a docStructure.Document derived object
			* a file name
			* a URL
			* a file-like object
			* '-' to specify stdin
			* None if data is to be passed in instead
		:param data: if filename is None, pass in a data buffer
		:param mimeType: since we may not have a filename to go off, specify the file type
		:param progressFn: called whenever progress changes
		:param statusFn: called whenever status sting changes
		:param processes: speed things up by running sentence checks on multiple cores.
			(Use only 1 when running interactively, or you could get out of order!)
		"""
		if not isinstance(doc,docStructure.Document):
			doc=docStructure.Document(doc)
		if statusFn==None:
			def statusFn(s):
				pass
		statusFn('Checking document problems...')
		class Shared():
			dp=self._docbprobs(doc)
		statusFn('Done checking document')
		sentences=doc.sentences
		sentNo=0
		statusFn('Checking sentence problems...')
		numSentences=len(sentences)
		lastPercent=-1
		def processSentence(sentNo):
			while True:
				sentence=sentences[sentNo]
				recheck=False
				for sp in self._sentprobs(sentence):
					# check all document problems before this sentence problem
					while len(Shared.dp)>0 and Shared.dp[0].start_idx<=sp.start_idx:
						d=Shared.dp.pop(0)
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
					Shared.dp=self._docbprobs(doc,start_idx=recheck)
				else:
					return
				if progressFn!=None:
					percent=int(100*sentNo/numSentences)
					if percent!=lastPercent:
						lastPercent=percent
						progressFn(percent)
		if processes<=1:
			for sentNo in range(numSentences):
				processSentence(sentNo)
		else:
			from Queue import Queue
			#from multiprocessing import Process
			from threading import Thread
			q=Queue()
			for sentNo in range(numSentences):
				q.put(sentNo)
			def processParallel():
				while True:
					sentence=q.get()
					processSentence(sentence)
					q.task_done()
			for i in range(processes):
				#px=Process(target=processParallel)
				px=Thread(target=processParallel)
				px.daemon=True
				px.start()
			q.join() # wait for everything to be eaten 
		statusFn('Done checking sentences.')
		statusFn('Checking remaining document problems...')
		# any remaining document problems	
		while len(Shared.dp)>0:
			d=Shared.dp.pop(0)
			if not self._allowProblem(d):
				continue
			repl=askUserFn(d)
			if repl!=None:
				sentence=sentence[0:d.start_idx]+repl+sentence[d.end_idx]
				sentences[sentNo]=sentence
				doc.sentences=sentences
				recheck=d.start_idx
				break
		statusFn('Done checking document.')
		
	def tkCheck(self,doc,data=None,mimeType=None):
		"""
		check the grammar and ask user for changes on the console (ncurses-based ui)
		
		:param doc: can be:
			* a docStructure.Document derived object
			* a file name
			* a URL
			* a file-like object
			* '-' to specify stdin
			* None if data is to be passed in instead
		:param data: if filename is None, pass in a data buffer
		:param mimeType: since we may not have a filename to go off, specify the file type
		"""
		import tkCheck
		tc=tkCheck.TkCheck()
		def onProblem(prob):
			subsys=prob.name
			options=prob.replacements
			errSentence,start_idx,end_idx=prob.excerpt()
			tc.errorBox(subsys,errSentence,start_idx,end_idx,options)
		tc.run(self.checkInteractive,onProblem,doc,data,mimeType,progressFn=tc.updatePercent,statusFn=tc.updateMessage)
		
	def ncCheck(self,doc,data=None,mimeType=None):
		"""
		check the grammar and ask user for changes on the console (ncurses-based ui)
		
		:param doc: can be:
			* a docStructure.Document derived object
			* a file name
			* a URL
			* a file-like object
			* '-' to specify stdin
			* None if data is to be passed in instead
		:param data: if filename is None, pass in a data buffer
		:param mimeType: since we may not have a filename to go off, specify the file type
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
		profile=False
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
						def p(s):
							if type(s)==int:
								print int(s)+'%'
							else:
								print s
						results=gc.check(arg[1],progressFn=p,statusFn=p)
						first=True
						for result in results:
							if first:
								print result.csvHeader
								first=False
							print result.csv
				elif arg[0]=='--ncCheck':
					if len(arg)<2:
						print 'ERR: Filename required for --ncCheck'
					else:
						print gc.ncCheck(arg[1])
				elif arg[0]=='--tkCheck':
					if len(arg)<2:
						print 'ERR: Filename required for --tkCheck'
					else:
						print gc.tkCheck(arg[1])
				elif arg[0]=='--profile':
					profile=True
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
		print '   --tkCheck=doc ..... interactive check in a window gui (use "-" to check from stdin)'
		print '   --check=doc ....... check entire doc and print all problems (use "-" to check from stdin)'
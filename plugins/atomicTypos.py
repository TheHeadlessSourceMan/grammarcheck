#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program detects spellchucker errors

TODO: the next step is to get part-of-speech detection involved
"""
from grammarcheck import *
import os


class ConfusedWords:
	"""
	represents a set of valid words that are commonly confused with one another
	"""
	
	def __init__(self,words=None,ranks=None,definitions=None):
		"""
		if words is a string, then split it into an array using the given splitter
		"""
		self.words=words
		if ranks==None:
			ranks=[]
			for i in range(len(words)):
				ranks.append(0.15+0.60*i/len(words))
		if len(ranks)!=len(ranks):
			raise Exception()
		self.ranks=ranks
		if definitions==None:
			definitions=[]
			for i in range(len(words)):
				definitions.append('')
		if len(definitions)!=len(words):
			raise Exception()
		self.definitions=definitions
		
	def check(self,word):
		"""
		returns a percent how likely the word is the wrong one
		0.0 = the word is definitely right
		1.0 = the word is definitely wrong
		-1 = we don't know that word
		"""
		try:
			idx=self.words.index(word)
		except ValueError:
			return None
		return self.ranks[idx]
		
	def __str__(self):
		ret=[]
		for i in range(len(self.words)):
			if self.definitions[i]!='':
				ret.append(self.words[i]+' - '+self.definitions[i])
			else:
				ret.append(self.words[i])
		return '\n'.join(ret)

		
class AtomicTypos(SentenceChecker):
	_CHECKS=None
	
	def __init__(self):
		SentenceChecker.__init__(self,'atomic_typos')
		if self._CHECKS==None:
			self._CHECKS=[]
			here=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep
			if True:
				f=open(here+'atomicTypos.csv','r')
				for line in f:
					line=[x.strip() for x in line.split(',',1)]
					self._CHECKS.append(ConfusedWords(line,[1.0,0.0]))
			if True:
				f=open(here+'confused_words.csv','r')
				for line in f:
					words=[]
					defs=[]
					for w in line.split('|'):
						w=[x.strip() for x in w.split('-',1)]
						words.append(w[0])
						if len(w)>1:
							defs.append(w[1])
						else:
							defs.append('')
					self._CHECKS.append(ConfusedWords(words,None,defs))
			if True:
				f=open(here+'homophones.csv','r')
				for line in f:
					self._CHECKS.append(ConfusedWords(line.split()))
	
	def checkSentence(self,doc):
		results=[]
		outOf=len(doc.words)
		badWords=0
		for w in doc.words:
			wordWasBad=False
			sw=str(w)
			for c in self._CHECKS:
				badness=c.check(sw)
				if badness>0:
					description=self.name+': '+sw+' could also be ['+(','.join(str(c).split('\n')))+']'
					results.append(DocProblem(description,w,badness))
					wordWasBad=True
			if wordWasBad:
				badWords+=1
		return results
		
	def __str__(self):
		ret=[]
		for c in self._CHECKS:
			ret.append(str(c))
		return '\n'.join(ret)

if __name__ == '__main__':
	import sys
	from docStructure import Document
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
				f=open(arg,'r')
				doc=Document(f.read())
				at=AtomicTypos()
				#print at
				for DocProblem in at.check(doc):
					print DocProblem
	if printhelp:
		print 'Usage:'
		print '  atomicTypos.py [options]'
		print 'Options:'
		print '   NONE'
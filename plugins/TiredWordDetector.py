"""
Check sentences for overused words.
"""
import os
from grammarcheck import *


class TiredWordDetector(SentenceChecker):
	"""
	Check sentences for overused words.
	"""
	overusedWordList=None

	def __init__(self,filename=None):
		if filename==None:
			filename=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep+'overusedWords.csv'
		SentenceChecker.__init__(self,'tired_word_detector')
		if self.overusedWordList==None:
			f=open(filename,'r')
			self.overusedWordList={}
			for line in f:
				line=[x.strip() for x in line.split('|',1)]
				if len(line)==2:
					self.overusedWordList[line[0]]=line[1]
		self.DocProblemRank=0.25
		if False:
			fixedWordList={}
			for k,v in self.overusedWordList.items():
				k=Word(k)
				fixedWordList[k.getRoot()]=v
			self.overusedWordList=fixedWordList
		
	def checkSentence(self,sentence):
		"""
		check a sentence for overused words
		
		returns [DocProblem]
		"""
		docProblems=[]
		for word in sentence.words:
			root=word.getRoot()
			if root in self.overusedWordList.keys():
				docProblems.append(DocProblem(self.overusedWordList[root],word,self.DocProblemRank))
		return docProblems
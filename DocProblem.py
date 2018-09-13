#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This class represents a potential grammar/spelling problem.
"""
from docStructure import DocFrag


class DocProblem(object):
	"""
	This class represents a potential grammar/spelling problem.
	"""
	
	def __init__(self,description='',atWord=None,severity=0,certainty=0.0,start_idx=0,end_idx=0,name='',replacements=[],fromChecker=None,doc=None):
		"""
		:param description: a description of the problem found
		:param atWord: so we can determine the location of the problem
		:param severity: how bad the problem is (a decimal percent)
		:param certainty: how certain we are that this really is a problem (a decimal percent)
		:param start_idx: start position of the problem
		:param end_idx: end position of the problem
		:param name: name of the problem
		:param replacements: suggested fixes (in preferred order) that can be pasted between start_idx and end_idx
		:param fromChecker: link to the checker tool which found this problem
		:param doc: the document where the problem resides
		"""
		self.description=description
		self.atWord=atWord # TODO: this should go away in favor of, say, a range to highlight in the document
		self.severity=severity
		self.certainty=certainty
		self.start_idx=start_idx
		self.end_idx=end_idx
		self.name=name
		self.replacements=replacements
		self.fromChecker=fromChecker
		self.doc=doc
		if not isinstance(doc,DocFrag):
			raise Exception("Invalid document type specified: "+doc.__class__.__name__)

	def excerpt(self):
		"""
		Get a document excerpt with the error highlighted
		
		:return: (text,startHighlight,endHighlight)
		"""
		ret=[]
		sLast=None
		startOffs=0
		for idx in range(self.start_idx,self.end_idx):
			s=self.doc.sentenceAt(self.start_idx)
			if sLast==None:
				startOffs=start_idx-s.start_idx
				ret.append(str(s))
				s=sLast
			elif s!=sLast:
				ret.append(str(s))
				sLast=s
		return (''.join(ret),startOffs,startOffs+(self.end_idx-self.start_idx))
		
	@property
	def location(self):
		"""
		:return: the location (line number) of the error within the document
		"""
		return self.doc.doc.offsToLine(self.start_idx)
		
	@property
	def csv(self):
		"""
		:return: the error as a row for a .csv spreadsheet
		"""
		location=self.location
		return ','.join([
			self.fromChecker.__class__.__name__,
			self.name,
			str(location[0]),str(location[1]),
			'"'+(','.join(self.replacements))+'"',
			'"'+self.description.replace('"',"'").replace('\n',' ').strip()+'"'])
		
	@property
	def csvHeader(self):
		"""
		:return: column labels to go in the first row of a .csv spreadsheet
		"""
		return 'checker,name,line,character,replacements,description'
		
	def __repr__(self):
		"""
		:return: textual representation of this problem
		"""
		location=self.atWord.descriptiveLocation(False)
		return 'LVL='+str(self.severity)+' At='+location+' Desc='+self.description
		
		
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
				print 'ERR: unknown argument "'+arg+'"'
	if printhelp:
		print 'Usage:'
		print '  DocProblem.py [options]'
		print 'Options:'
		print '   NONE'
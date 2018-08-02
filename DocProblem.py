class DocProblem(object):
	"""
	This class represents a potential grammar/spelling problem.
	"""
	
	def __init__(self,
		description='',
		atWord=None,
		severity=0,
		certainty=0.0,
		start_idx=0,
		end_idx=0,
		name='',
		replacements=[], # in preferred order
		fromChecker=None, # who caught this problem
		doc=None
		):
		self.description=description
		self.atWord=atWord # TODO: this should go away
		self.severity=severity
		self.certainty=certainty # how certain we are that this an error
		self.start_idx=start_idx
		self.end_idx=end_idx
		self.name=name
		self.replacements=replacements # in preferred order
		self.fromChecker=fromChecker # who caught this problem
		self.doc=doc # the doc this error is in

	def excerpt(self):
		"""
		Get a document excerpt with the error highlighted
		
		returns (text,startHighlight,endHighlight)
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
		
	def __str__(self):
		location=self.atWord.descriptiveLocation(False)
		return 'LVL='+str(self.severity)+' At='+location+' Desc='+self.description
#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Overuse of be verbs (such as "was") is a good indication of telling, not showing
"""
from grammarcheck import *
from docStructure import re


was_alternatives=['abided','abode','assembled','balanced','basked','bent','blanketed','blocked','burrowed','choked','collected','colonized','convened','covered','cowered','cozied up','crouched','curled up','crammed','crowded','dawdled','dozed','drooped','existed','filled','floated','flocked','flooded','gathered','harbored','heaped','hid','hovered','huddled','hung around','idled','inhabited','inundated','jammed','knelt','lay','lazed','lined','lingered','lived','lodged','lolled','lounged','massed','met','mounded','nestled','occupied','packed','perched','piled','poised','populated','posed','postured','reclined','relaxed','remained','reposed','resided','rested','reunited','roomed','roosted','sagged','sat','saturated','settled','sheltered','slept','slouched','slumbered','slumped','snoozed','sojourned','sprawled','spread-eagled','squished','squeezed','stacked','stayed','stood','stooped','stretched out','stuck','sunned','swamped','swarmed','teemed','tenanted','thronged','unwound','waited','wallowed','wedged','wilted']


class WasBuster(SentenceChecker):
	"""
	Overuse of be verbs (such as "was") is a good indication of telling, not showing
	"""
	
	regex=None
	regex2=None
	
	def __init__(self):
		SentenceChecker.__init__(self,'Bad_Content_Finder')
		if self.regex==None:
			regex=r"""((there\s+(is|was|will\s+be)\s+)([^\."!?]+?)(\s+(who|that|which)))(.*)"""
			self.regex=re.compile(regex,re.IGNORECASE|re.DOTALL)
			regex2=r"""(is|am|was|will\s+be)\s+([a-z]+?)(ing\s+)"""
			self.regex2=re.compile(regex2,re.IGNORECASE|re.DOTALL)

	def checkSentence(self,sentence):
		"""
		More ideas:
			https://kathysteinemann.com/Musings/to-be/
		"""
		ret=[]
		if sentence.endswith('?'):
			return ret
		m=self.regex.match(sentence)
		if m!=None:
			err=DocProblem(
				description='Unnecessary "be" verb clause',
				atWord=None,
				severity=0,
				certainty=0.0,
				start_idx=0,
				end_idx=len(m.group(1)),
				name='',
				replacements=[m.group(1).group(2)[0].upper()+m.group(1).group(2)[1:]], # in preferred order
				fromChecker=self, # who caught this problem
				doc=sentence
				)
			ret.append(err)
			return ret
		m=self.regex2.find(sentence)
		if m!=None:
			if regex2.group(1)=='is': # is fighting => fights
				sugg=m.group(2)+'s'
			elif regex2.group(1)=='am': # am fighting => fight
				sugg=m.group(2)
			elif regex2.group(1)=='was': # was fighting => fighted
				sugg=m.group(2)+'ed' # TODO: some are special, eg run is not runned, but ran... not fighted, but fought
			elif regex2.group(1).startswith('will'): # will be fighting => will fight
				sugg='will '+m.group(2)
			err=DocProblem(
				description='Passive "be"',
				atWord=None,
				severity=0,
				certainty=0.0,
				start_idx=m.group(0).start(),
				end_idx=m.group(0).end(),
				name='',
				replacements=[sugg], # in preferred order
				fromChecker=self, # who caught this problem
				doc=sentence
				)
			ret.append(err)
			return ret
		if 'was' in sentence:
			err=DocProblem(
				description="""
					"Was" problem. "X was thus" is weak, dull, and passive.
						* details! why X was thus?  what word describes what is going on?
						* what action is going on?  describe it.
					""",
				atWord=None,
				severity=0,
				certainty=0.0,
				start_idx=0,
				end_idx=len(m.group(1)),
				name='',
				replacements=[was_alternatives], # in preferred order
				fromChecker=self, # who caught this problem
				doc=sentence
				)
			ret.append(err)
			return ret
		isa='is a'
		pos=sentence.find(isa)
		if pos>=0:
			err=DocProblem(
				description="""
					You can make "he is a ___" more active.  Instead of saying what it is, describe what happens, eg,
						"he is a fighter" => "he fights at the local Y"
					""",
				atWord=None,
				severity=0,
				certainty=0.0,
				start_idx=pos,
				end_idx=len(isa),
				name='',
				replacements=[], # in preferred order
				fromChecker=self, # who caught this problem
				doc=sentence
				)
			ret.append(err)
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
		print '  NONE'

#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Had is a weak word, and a good indication of telling
"""
from grammarcheck import *
from docStructure import re

had_alternatives=['accommodate','accumulate','acquire','adopt','appropriate','assume','attain','be adorned with','be blessed with','be born with','be decorated with','be endowed with','be favored with','be in possession of','be possessed of','be privileged with','be the owner of','bear','benefit from','boast','brandish','bring','broadcast','buy','care for','carry','clasp','cling to','clutch','collect','comprise','conceal','confiscate','consume','contain','contribute','control','convey','cultivate','defend','disclose','display','enclose','encompass','endure','enjoy','exhibit','experience','expose','fall heir to','feature','flail','flash','flaunt','flourish','garb oneself in','get','get pleasure from','grab','grapple','grasp','grip','handle','hang on to','harbor','haul','hoard','hog','hold','hold on to','hold title to','house','imprison','include','incorporate','keep','keep hold of','keep possession of','latch on to','lay claim to','look after','maintain','manage','manifest','nurture','obtain','own','palm','parade','possess','procure','purchase','put on','put on display','put on view','reap the benefit of','retain','reveal','rule','salt away','secure','seize','show off','sport','squirrel away','stock','stockpile','store','stow','strut','suffer','support','sustain','take hold of','take pleasure in','teem with','transport','trumpet','undergo','unveil','vaunt','wag','wave','wear']


class HadBlaster(SentenceChecker):
	"""
	Had is a weak word, and a good indication of telling
	"""
	
	def __init__(self):
		SentenceChecker.__init__(self,'Bad_Content_Finder')

	def checkSentence(self,sentence):
		"""
		"""
		ret=[]
		had=sentence.findword('had')
		if had.next=='on': # had on => wore
			err=DocProblem(
				description='"had on" is sometimes a low-information phrase',
				atWord=None,
				severity=0,
				certainty=0.0,
				start_idx=had.start,
				end_idx=had.next.end,
				name='',
				replacements=[had_alternatives], # in preferred order
				fromChecker=self, # who caught this problem
				doc=sentence
				)
			ret.append(err)
			return ret
		if had.next in ['always','never','been']:
			err=DocProblem(
				description='"had always/never been" is somewhat passive. suggestion: delete it!',
				atWord=None,
				severity=0,
				certainty=0.0,
				start_idx=had.start,
				end_idx=had.next.end,
				name='',
				replacements=[], # in preferred order
				fromChecker=self, # who caught this problem
				doc=sentence
				)
			ret.append(err)
			return ret
		if had.next in ['a','an','some','several']:
			err=DocProblem(
				description='"had" for posession is ok, but there is often a more descriptive word "the dog had a bone" => "the dog gnawed on a bone"',
				atWord=None,
				severity=0,
				certainty=0.0,
				start_idx=had.start,
				end_idx=had.next.end,
				name='',
				replacements=[], # in preferred order
				fromChecker=self, # who caught this problem
				doc=sentence
				)
			ret.append(err)
			return ret
		err=DocProblem(
			description="""
				had is bad.
				suggestion: describe how we know, eg "he had been a fighter" => "he bore the characteristic busted known of a trained boxer"
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
		print '   NONE'

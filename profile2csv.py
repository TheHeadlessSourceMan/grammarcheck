#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program converts a profile dump to a csv file
"""
import pstats,StringIO


def profile2csv(filename):
	"""
	Convert a python profile dump to a useable .csv spreadsheet
	
	See also:
		https://docs.python.org/3/library/profile.html
	"""
	result=StringIO.StringIO()
	pstats.Stats(filename,stream=result).print_stats()
	result=result.getvalue()
	# split up the process output into CSV data
	result='ncalls'+result.split('ncalls')[-1].replace('{','"{').replace('}','}"')
	result='\n'.join([','.join(line.rstrip().split(None,6)) for line in result.split('\n')])
	# barf it out to a file
	output=filename.rsplit('.')[0]+'.csv'
	f=open(output,'w')
	f.write(result)
	f.close()
	print 'Saved to '+output

	
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
				if arg[0] in ['-h','--help']:
					printhelp=True
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				profile2csv(arg)
	if printhelp:
		print 'Usage:'
		print '  profile2csv.py [options] [file]'
		print 'Options:'
		print '   NONE'
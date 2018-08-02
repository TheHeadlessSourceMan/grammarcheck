#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program performs a grammar check
"""
import os
import threading
import subprocess
import urllib,urllib2
import lxml.etree
import time

HERE=os.path.abspath(__file__).rsplit(os.sep,1)[0]

class GrammarError(object):
	"""
	A single error
	"""
	
	def __init__(self,xml):
		self._xml=xml
	
	def _quickget(self,name):
		e=self._xml.find(name)
		if e==None:
			return ''
		return e.text
	
	@property
	def string(self):
		return self._quickget('string')
	
	@property
	def precontext(self):
		return self._quickget('precontext')
	
	@property
	def type(self):
		return self._quickget('type')
	
	@property
	def description(self):
		return self._quickget('description')
	
	@property
	def suggestions(self):
		e=self._xml.find('suggestions')
		if e==None:
			return []
		return [option.text for option in e]
	@property
	def options(self):
		return self.suggestions
	
	def __str__(self):
		ret=[self.type+' error:']
		ret.append('"'+self.precontext+' '+self.string+'"')
		ret.append(self.description)
		for o in self.options:
			ret.append('\t'+o)
		return '\n\t'.join(ret)
		
	
class GrammarCheck(object):
	"""
	This program performs a grammar check using ATD (After The Deadline)
	grammar checker.  If the server is running, we'll use it.  If not, start one.
	"""
	
	def __init__(self,ip='127.0.0.1',port=1049,lowmem=True,serverDebug=True):
		self.ip=ip
		self.port=port
		self.lowmem=lowmem
		self.serverDebug=serverDebug
		self._serverThread=None
		self._server=None
		self._serverReady=False
		
	def _startServer(self):
		if self._serverThread!=None:
			return
		self._serverThread=threading.Thread(None,self._serverThreadFn)
		self._serverReady=False
		self._serverThread.start()
		while not self._serverReady:
			time.sleep(0.01)
		
	def __del__(self):
		self._stopServer()
		
	def _stopServer(self):
		if self._server!=None:
			self._server.kill()
	
	def _serverThreadFn(self):
		cmd="""java -Dfile.encoding=UTF-8 -XX:+AggressiveHeap -XX:+UseParallelGC -Datd.lowmem="""+str(self.lowmem).lower()+""" -Dbind.interface="""+self.ip+""" -Dserver.port="""+str(self.port)+""" -Dsleep.classpath=$ATD_HOME/lib:$ATD_HOME/service/code -Dsleep.debug=24 -classpath .\lib\sleep.jar;.\lib\moconti.jar;.\lib\spellutils.jar httpd.Moconti atdconfig.sl"""
		cmd=cmd.replace('\n',' ')
		print "Starting server on "+self.ip+':'+str(self.port)
		self._server=subprocess.Popen(cmd,shell=False,cwd=HERE+os.sep+'atd',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		last=None
		while self._server.poll() is None:
			line=self._server.stdout.readline().rstrip()
			if self.serverDebug:
				if line=='' and line==last:
					continue
				print line
				last=line
			if line.find('Models loaded')>0:
				self._serverReady=True
		self._serverThread=None
		self._server=None
		
	def checkFile(self,f):
		"""
		file can be a file-like object or filename
		
		returns [GrammarError]
		"""
		if type(f) in (str,unicode):
			f=open(f,'rb')
		return self.check(f.read())

	def check(self,text):
		"""
		Text should be a single sentence.
		
		returns [GrammarError]
		"""
		key=os.getpid()
		url='http://'+self.ip+':'+str(self.port)+'/checkDocument?key='+str(key)
		url+='&data='+urllib.quote_plus(text)
		try:
			f=urllib2.urlopen(url)#,text)
		except urllib2.URLError:
			self._startServer()
			f=urllib2.urlopen(url)#,text)
		if f.getcode()!=200:
			raise Exception('server returned error code '+str(f.getcode()))
		result=lxml.etree.fromstring(f.read())
		return [GrammarError(e) for e in result.findall(".//error")]
		
		
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
		gc=GrammarCheck()
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				for e in gc.checkFile(arg):
					print str(e)
				gc._stopServer()
	if printhelp:
		print 'Usage:'
		print '  grammarcheck.py [options] doc.txt'
		print 'Options:'
		print '   NONE'
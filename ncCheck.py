#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is an nurses ui for grammarcheck
"""
try:
	import curses
except ImportError,e:
	print 'ERR: missing curses.  Get it here:'
	print '   https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses'
	raise e
import sys,time

class NcCheck(object):
	def __init__(self):
		self.screen=None
	
	def _onEnd(self):
		if self.screen!=None:
			self.screen.clear()
			curses.nocbreak()
			self.screen.keypad(0)
			curses.echo()
			curses.endwin()
			self.screen=None
		
	def _onStart(self):
		if self.screen==None:
			self.screen=curses.initscr()
			curses.noecho()
			curses.cbreak()
			self.screen.keypad(True)
			curses.start_color()
			curses.init_pair(1,curses.COLOR_WHITE,curses.COLOR_BLUE)
			self.screen.box()
			self.screen.refresh()
			
	def _alertBox(self,options):
		defaultSelections=[
			'a - apply all',
			'i - ignore rule',
			's - skip once',
			'[esc] - abandon checking'
			]
		height=len(options)+len(defaultSelections)+3
		width=len('[esc] - abandon checking')+2
		begin_y=7
		begin_x=self.screen.getmaxyx()[1]/2-width/2
		self.alertBox=curses.newwin(height,width,begin_y,begin_x)
		self.alertBox.box()
		idx=1
		for i in range(len(options)):
			self.alertBox.addstr(idx,1,str(i)+' - '+options[i],curses.color_pair(1))
			idx+=1
		self.alertBox.addstr(idx,0,chr(198)+(chr(205)*(width-2))+chr(181),curses.color_pair(1))
		idx+=1
		for i in range(len(defaultSelections)):
			self.alertBox.addstr(idx,1,defaultSelections[i],curses.color_pair(1))
			idx+=1
		self.alertBox.refresh()
		
	def run(self,subsys='spelling',errSentence="The directions from his huose to mine",start_idx=24,end_idx=29,options=[]):
		try:
			self._onStart()
			self.screen.bkgdset(' ',curses.color_pair(1))
			self.screen.addstr(0,0,'grammarcheck - '+subsys+':',curses.color_pair(1)|curses.A_STANDOUT)
			x_indent=3
			y_indent=2
			self.screen.addstr(y_indent,x_indent,errSentence[0:start_idx],curses.A_DIM)
			self.screen.addstr(y_indent,start_idx+x_indent,errSentence[start_idx:end_idx],curses.A_STANDOUT)
			self.screen.addstr(y_indent,end_idx+x_indent,errSentence[end_idx:],curses.A_DIM)
			self._alertBox(options)
			applyAll=False
			while True:
				c=self.screen.getch()
				if c==ord('a'): # apply all #TODO:
					applyAll=True
				elif c==ord('i'): # ignore all #TODO:
					return None
				elif c==ord('s'): # skip once
					return None
				elif c>=ord('0') and c<=ord('9'):
					c-=ord('0')
					if c<len(options):
						return options[c]
				elif c==27: # escape
					break
				else:
					print c
			self._onEnd()
		except:
			self._onEnd()
			raise

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
				nc=NcCheck()
				nc.run()
				#print 'ERR: unknown argument "'+arg+'"'
	if printhelp:
		print 'Usage:'
		print '  ncCheck.py [options]'
		print 'Options:'
		print '   NONE'
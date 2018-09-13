#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This is a tkinter ui for grammarcheck
"""
from Tkinter import *
from ttk import *
import sys,time


class TkCheck(object):
	def __init__(self):
		self._alertbox=None
		self.tk=Tk()
		popup=Toplevel(width=300,height=200)
		self.messageVar=StringVar()
		Label(popup, text=self.messageVar).grid(row=0,column=0)
		progress = 0
		self.progressVar = DoubleVar()
		progress_bar = Progressbar(popup, variable=self.progressVar, maximum=100)
		progress_bar.grid(row=1, column=0)#.pack(fill=tk.X, expand=1, side=tk.BOTTOM)
		popup.pack_slaves()
	
	def _onEnd(self):
		pass # TODO
		
	def _onStart(self):
		pass # TODO
			
	@property
	def alertBox(self):
		if self._alertbox==None:
			self._alertbox=Toplevel()
			self.messageCtl=Text ( self._alertbox)
			self.messageCtl.pack()
			b = Button(self.alertbox, text="a - apply all", command=self.applyAll)
			b.pack()
			b = Button(self.alertbox, text="i - ignore rule", command=self.ignoreRule)
			b.pack()
			b = Button(self.alertbox, text="s - skip once", command=self.skipOnce)
			b.pack()
			b = Button(self.alertbox, text="[esc] - abandon checking", command=self.abandonChecking)
			b.pack()
			self._alertbox.pack_slaves()
		return self._alertbox

	def updateMessage(self,str):
		self.messageVar.set(str)
		
	def updatePercent(self,percent):
		progressVar.set(progress)
		
	def errorBox(self,subsys='spelling',errSentence="The directions from his house to mine",start_idx=24,end_idx=29,options=[]):
		alertbox=self.alertbox
		self.messageCtl.insert(INSERT,errSentence)
		self.messageCtl.tag_add("problem",start_idx,end_idx)
		self.messageCtl.tag_config("problem", background="yellow")
		
	def run(self,grammarcheckFn,*args):
		self._onStart()
		self.tk.mainloop()
		self._onEnd()

			
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
		print '  tkCheck.py [options]'
		print 'Options:'
		print '   NONE'
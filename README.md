# grammarcheck
![Status: Stable](https://img.shields.io/badge/status-stable-green.svg?style=plastic)
![Python Version: 2.7](https://img.shields.io/badge/Python%20Version-2.7-blue.svg?style=plastic)
![Release Version: 1.0](https://img.shields.io/badge/Release%20Version-1.0-green.svg?style=plastic)
[![webpage:click here](https://img.shields.io/badge/webpage-click%20here-blue.svg?style=plastic)](https://theheadlesssourceman.wordpress.com/2018/08/02/grammarcheck/)

License - LGPL

A simple, pluggable, python spelling/grammar checker.  Works automatically with marked-up stuff.


Rant:
-----
The grammar checker tools out there are surprisingly bad.  They give a lot of false-positives based on technical rules ("I am.", answered Bob.) and yet still don't clean up crappy writing. (The tree was big.  The tree was good.  It was a big, good, tree.) 


Status:
-------
Many of the individual tools work, but I really need a smart grammar parser like "bllip" to proceed.
	
TODO:
-----
* need a duplicate phrase finder capable of detecting "the cat toyed with the with the mouse"
* use grammar sense to separate mistakes like "would you like his one" = "this one"
* Should use something like NLTK or PANDAS
* Differentiate between strict and conversational English. (Use more conversational in sentences).
* Ability to split sentences up short and snappy as possible
* Autodetect common spell-chucker problems
* Auto fix repeated words
* Integrate with openoffice
* How to detect missing "that" as in "The change of light was so sudden [THAT] it made Bob blink.  He stumbled inside hoping to get out of the way so [THAT] the others wouldn’t run into him."
* wordification of things like "what so ever" and "none the less"
* detect the correct homophones  "Whether"=>"weather"  "Tale"=>"tail", "to"=>"too"=>"two"
* somehow make verb tenses match
* A good name for this when done might be "pudding", as in, "the proof is in the pudding"
* detect when more scene description is necessary (smell,sound,feel,grit,light...)


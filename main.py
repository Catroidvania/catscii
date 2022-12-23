# a kwik n dirty ascii animation program
# made with catroidvania
# first created 2 12 22
# verison 1.4
# version released 8 12 2022

# based on the makeyourowntexteditor found on viewsourcecode.org
# but now its python lol

# for getting out the file number of the terminal
from sys import stdin
# for reading by byte
import os
# for modifying the tty attributes
import termios
# for checking character input type
# import unicodedata as unidata
# for getting terminal data
from fcntl import ioctl
# for storing the ioctl return because this is actually ass
from struct import pack, unpack
# time
from time import time, sleep
# random (:
#from random import choice
# for our drawing functions
# from math import cos, sin, tan


def clearCanvas(width=80, height=24, fillchar=" "):
	# does well, clearing buffer stuff
	return [
		[fillchar for col in range(width)] for row in range(height)]


def drawToCanvas(canvas, x, y, content, canvasWidth=None, contentWidth=None):
	# draws individual elements to the buffer

	# if none are supplied
	if not canvasWidth: canvasWidth = len(canvas[0])-1
	if not contentWidth: contentWidth = len(content[0])-1

	# so we dont need to calculate on every iter
	canvasHeight = len(canvas)-1
	contentHeight = len(content)-1

	# draw for each line
	for row,line in enumerate(canvas):
		# so we dont off the bottom
		if row + y > canvasHeight: break
		# so we dont try and index nonexistant lines
		if row > contentHeight: break
		# so we dont draw off the side
		if contentWidth > canvasWidth:
			canvas[row+y][x:canvasWidth] = content[row][:canvasWidth-x]
		elif contentWidth < canvasWidth:
			canvas[row+y][x:] = content[row] + canvas[row+y][contentWidth+x+1:]
		else:
			canvas[row+y][x:] = content[row]

	return canvas


def printToCanvas(canvas, x, y, string, canvasWidth=None):
	# print a string to the canvas

	# if none are supplied
	if not canvasWidth: canvasWidth = len(canvas[0])-1
	contentWidth = len(string)-1

	# write to buffer row
	# so we dont draw off the edge
	if contentWidth > canvasWidth:
		canvas[y][x:] = string[:canvasWidth-x]
	elif contentWidth < canvasWidth:
		canvas[y][x:] = list(string) + canvas[y][contentWidth+x+1:]
	else:
		canvas[y][x:] = string[:canvasWidth-x]

	return canvas


def drawCursor(canvas, x, y, blink=False):
	# draws the cursor as inverted text
	cursor = "\033[7m" + canvas[y][x] + "\033[0m"

	if blink: cursor = "\033[5m" + cursor

	canvas[y][x] = cursor

	return canvas


def drawScreen(unitno, canvas, height=None):
	# draws the buffer to screen

	# if none if supplied
	if not height: height = len(canvas)-1

	# putting it all in one string
	try:
		# add clear screen, move to top of screen
		stringbuf = "\033[H\033[?25l"
		for row,line in enumerate(canvas):
			# add clear line char and content
			if row > 0: stringbuf += "\033[K"
			# add buffer row
			stringbuf += "".join(line)
			# add a newline
			if row < height: stringbuf += "\r\n"

		os.write(unitno, stringbuf.encode("utf-8"))
	except Exception as exc:
		os.write(unitno, str(exc).encode("utf-8"))


def getFromCanvas(canvas, x1, y1, x2, y2, canvasWidth=None):
	# returns the contents of the bufer from x1, y1 to x2, y2
	canvasHeight = len(canvas)-1
	if not canvasWidth: canvasWidth = len(canvas[0])-1

	# ensures the second mark is on the correct row
	x2 += 1
	y2 += 1

	# make sure we can actually index the canvas
	if x1 > x2: x1,x2 = x2,x1
	if y1 > y2: y1,y2 = y2,y1

	# so no index error; shoulndt even be possible to do lmao
	if x1 < 0: x1 = 0
	if y1 < 0: y1 = 0
	if x2 > canvasWidth: x2 = canvasWidth
	if y2 > canvasHeight: y2 = canvasHeight

	# get y rows
	selected = canvas[y1:y2]

	# get x cols
	for row,line in enumerate(selected):
		selected[row] = line[x1:x2]

	return selected


def drawPoints(canvas, points, fillchar="#"):
	# draws a list of points onto the canvas
	for point in points:
		canvas[point[1]][point[0]] = fillchar

	return canvas


def fillByChar(canvas, x, y, fillchar="#"):
	pass


def drawLine(canvas, x1, y1, x2, y2, fillchar="#"):
	# draws a line across the canvas
	# because we can only draw left to right
	if x1 > x2:
		x1,x2 = x2,x1
		y1,y2 = y2,y1

	points = []
	point = 0

	# god this code feels so bad
	# why is linear equations the hardest thing ive ever done???
	if not (x2 - x1):
		height = max(y2, y1) - min(y1, y2)
		facing = -1 if y1 > y2 else 1
		while point <= height:
			points.append((x1, (point*facing)+y1))
			point += 1
	elif not (y2 - y1):
		width = max(x2, x1) - min(x1, x2)
		facing = -1 if y1 > y2 else 1
		while point <= width:
			points.append(((point*facing)+x1, y1))
			point += 1
	else:
		width = x2 - x1
		height = y2 - y1
		slope = height / width
		prescision = 1/max(width, height)

		while point <= width:
			points.append((round(point)+x1, round(slope*point)+y1))
			point += prescision

	canvas = drawPoints(canvas, points, fillchar)
	return canvas
	# and to think there is most certainly a library for all of this


def drawBox(canvas, x1, y1, x2, y2, fillchar="#"):
	# draws a buncha lines that make a box
	canvas = drawLine(canvas, x1, y1, x1, y2, fillchar=fillchar)  # left
	canvas = drawLine(canvas, x1, y1, x2, y1, fillchar=fillchar)  # top
	canvas = drawLine(canvas, x2, y1, x2, y2, fillchar=fillchar)  # right
	canvas = drawLine(canvas, x1, y2, x2, y2, fillchar=fillchar)  # bottom

	return canvas


def drawSolidBox(canvas, x1, y1, x2, y2, fillchar="#"):
	pass


def drawTriangle(canvas, x1, y1, x2, y2, x3, y3, fillchar="#"):
	# draw triangle witha buncha lines
	canvas = drawLine(canvas, x1, y1, x2, y2, fillchar=fillchar)
	canvas = drawLine(canvas, x2, y2, x3, y3, fillchar=fillchar)
	canvas = drawLine(canvas, x1, y1, x3, y3, fillchar=fillchar)

	return canvas


def drawCurve(canvas, x1,y1, x2,y2, x3,y3, t, prescision=0.01, fillchar="#"):
	# draws a bezier curve based on the mark and cursor position

	if x1 > x2 :
		x1,x2 = x2,x1
		y1,y2 = y2,y1

	points = []
	t = 0

	while t <= 1:
		points.append(
			(round(quadBezierCurve(x1, x3, x2, t)),
			round(quadBezierCurve(y1, y3, y2, t))))

		t += prescision

	canvas = drawPoints(canvas, points, fillchar)
	return canvas


def quadBezierCurve(p1, p2, p3, t):
	# quick helper function for doing the bezier math
	return ((1-t)**2)*p1 + 2*(1-t)*t*p2 + (t**2)*p3


def cubicBezierCurve(p1, p2, p3, p4, t):
	# another helper function for drawing circles because i cannot
	# figure out how to graph ellipses lmao
	# not even sure if this is needed
	# no it isnt but its cool
	return ((1-t)**3)*p1 + 3*((1-t)**2)*t*p2 + 3*(1-t)*(t**2)*p3 + (t**3)*p4


def drawElipse(canvas, x1, y1, x2, y2, prescision=0.01, fillchar="#"):
	# draws an ellipse with a set of quadratic bezier curves

	if x1 > x2 :
		x1,x2 = x2,x1
		y1,y2 = y2,y1

	points = []
	t = 0

	# for drawing from box boundries
	midx = round((max(x1, x2) - min(x1, x2)) / 2 + min(x1, x2))
	midy = round((max(y1, y2) - min(y1, y2)) / 2 + min(y1, y2))


	while t <= 1:

# with quad bezier; not prefered because it runs more calculations
# might have to find a better solution later on
		# top left
		points.append(
			(round(quadBezierCurve(x1, x1, midx, t)),
			round(quadBezierCurve(midy, y1, y1, t))))
		# top right
		points.append(
			(round(quadBezierCurve(midx, x2, x2, t)),
			round(quadBezierCurve(y1, y1, midy, t))))
		# bottom right
		points.append(
			(round(quadBezierCurve(midx, x2, x2, t)),
			round(quadBezierCurve(y2, y2, midy, t))))
		# bottom left
		points.append(
			(round(quadBezierCurve(x1, x1, midx, t)),
			round(quadBezierCurve(midy, y2, y2, t))))


# avec cubic bezier; because its cool sounding
# ellipses do not reach to the top/bottom edge tho :///
		# top half
#		points.append(
#			(round(cubicBezierCurve(x1, x1, x2, x2,  t)),
#			round(cubicBezierCurve(midy, y1, y1, midy, t))))
		# bottom half
#		points.append(
#			(round(cubicBezierCurve(x1, x1, x2, x2, t)),
#			round(cubicBezierCurve(midy, y2, y2, midy, t))))

		t += prescision

	canvas = drawPoints(canvas, points, fillchar)
	return canvas


# unused :///
def drawElipse2(canvas, x1, y1, x2, y2, x3, y3, prescision=0.01, fillchar="#"):
	# draws an ellipse with a set of quadratic bezier curves

	# unsure if needed for ellipses
	if x1 > x2 :
		x1,x2 = x2,x1
		y1,y2 = y2,y1

	points = []
	t = 0
	
	# for drawing with arbitrary rotation
	xshiftx = round((x1 - x2) / 2)
	xshifty = round((y1 - y2) / 2)
	
	yshiftx = round(x3 - x1 + xshiftx)
	yshifty = round(y3 - y1 + xshifty)

	x4 = x1 - xshiftx - yshiftx
	y4 = y1 - xshifty - yshifty

	while t <= 1:	
		# arbitrary rotation!
		# top left
		points.append(
			(round(quadBezierCurve(x1, x1+yshiftx, x3, t)),
			round(quadBezierCurve(y1, y1+yshifty, y3, t))))
		# top right
		points.append(
			(round(quadBezierCurve(x3, x2+yshiftx, x2, t)),
			round(quadBezierCurve(y3, y2+yshifty, y2, t))))
		# bottom right
		points.append(
			(round(quadBezierCurve(x2, x2-yshiftx, x4, t)),
			round(quadBezierCurve(y2, y2-yshifty, y4, t))))
		# bottom left
		points.append(
			(round(quadBezierCurve(x4, x1-yshiftx, x1, t)),
			round(quadBezierCurve(y4, y1-yshifty, y1, t))))
		
		t += prescision

	canvas = drawPoints(canvas, points, fillchar)
	return canvas


def handleInput(key):
	# seperates regualr keys from control keys etc
	# TODO do not have access to all keys like home / end / page up;down etc
	# and turns keypresses into strings
	if not key: return ""

	# arrow keys
	if key == b"\033[A": return "UPARROW"
	if key == b"\033[B": return "DOWNARROW"
	if key == b"\033[C": return "RIGHTARROW"
	if key == b"\033[D": return "LEFTARROW"
	# shift arrow keys
	if key == b"2A": return "SHIFTUPARROW"
	if key == b"2B": return "SHIFTDOWNARROW"
	if key == b"2C": return "SHIFTRIGHTARROW"
	if key == b"2D": return "SHIFTLEFTARROW"
	# ctrl shift arrow keys omg
	if key == b"6A": return "CTRLSHIFTUPARROW"
	if key == b"6B": return "CTRLSHIFTDOWNARROW"
	if key == b"6C": return "CTRLSHIFTRIGHTARROW"
	if key == b"6D": return "CTRLSHIFTLEFTARROW"


	# control characters

	# ctrl keys
	# if these are allowed to go through it gives an empty string
	# may rename these to thier respective ctrl shorthands
	if key == b"\x00": return "^@"	# set mark
	if key == b"\x01": return "^A"	# jump to first frame
	if key == b"\x02": return "^B"	# center cursor horizontally
	if key == b"\x03": return "^C"	# cursor to bottom edge
	if key == b"\x04": return "^D"	# jump to last frame
	if key == b"\x05": return "^E"	# draw ellipses
	if key == b"\x06": return "^F"	# enter terminal mode
	if key == b"\x07": return "^G"	# execute command
	if key == b"\x08": return "^H"	# delete frame
	if key == b"\x09": return "^I"	# tab
	if key == b"\x0A": return "^J"	# insert frame left
	if key == b"\x0B": return "^K"	# insert frame right
	if key == b"\x0C": return "^L"	# duplicat frame
	if key == b"\x0D": return "^M"	# enter
	if key == b"\x0E": return "^N"	# center cursor vertically
	if key == b"\x0F": return "^O"	# copy
	if key == b"\x10": return "^P"	# paste
	if key == b"\x11": return "^Q"	# quit program without saving
	if key == b"\x12": return "^R"	# draw box
	if key == b"\x13": return "^S"	# toggle playback mode
	if key == b"\x14": return "^T"	# draw triangle
	if key == b"\x15": return "^U"	#
	if key == b"\x16": return "^V"	# cursor to right edge
	if key == b"\x17": return "^W"	# draw line
	if key == b"\x18": return "^X"	# cursor to top edge
	if key == b"\x19": return "^Y"	# draw curve
	if key == b"\x1A": return "^Z"	# cursor to left edge
	if key == b"\x1B": return "^["	# change frame left
	if key == b"\x1C": return "^\\"	# append frame
	if key == b"\x1D": return "^]"	# change frame right
	if key == b"\x1E": return "^^"	#
	if key == b"\x1F": return "^_"	# cut
	if key == b"\x7F": return "^?"	# backspace

	# return as the letter if just a character
	return key.decode("utf-8", errors="replace")


def resizeAnimation(project, width, height):
	# a quick function to make sure a project is the right size
	correctsize = [[
		[" " for col in range(width)] for row in range(height)]
		for f in range(len(project))]

	for f,fr in enumerate(project):
		for r,row in enumerate(fr):
			for c,ch in enumerate(row):
				correctsize[f][r][c] = ch

	return correctsize


def saveAnimation(args):
	# saving an animation
	args += ["","","","",""]

	# param checking
	if not args[1] or args[1] == " ":
		frames = [[]]
	else:
		frames = args[1]

	if not args[2] or args[2] == " ":
		filename = "untitled" + str(time_ns()) + ".txt"
	else:
		filname = args[2]

	if not args[3] or args[3] == " ":
		raise ValueError("invalid width parameter!")
	else:
		width = int(width)

	if not args[4] or args[4] == " ":
		raise ValueError("invalid height parameter!")
	else:
		height = int(height)

	if not args[5] or args[5] == " ":
		linesep = "@@"
	else:
		linesep = args[5]

	stringframes = ""

	for frame in frames:
		stringframe = ""
		for f,row in enumerate(frame):
			if f > height: break
			#if f == 0: continue
			stringframe += "".join(row[:width]) + "\n"
		if stringframe: stringframes += stringframe + linesep + "\n"

	with open(filename, "w") as file:
		file.write(stringframes)


def loadAnimation(args):
	# load an animation
	args += ["",""]


	# param checking
	if not args[1] or args[1] == " ":
		raise ValueError("filename required!")
	else:
		filename = args[1]

	if not args[2] or args[2] == " ":
		linesep = "@@"
	else:
		linesep = args[2]

	with open(filename, "r") as file:
		contents = []
		frame = []
		while True:
			line = file.readline()
			if not line: break
			if line[-1] == "\n": line = line[:-1]
			if line == linesep:
				contents.append(frame)
				frame = []
			else:
				frame.append(line)

	return contents


# main program code
try:

	# version info
	version = 1.4

	# gets the file number of the terminal this is run in
	unit = stdin.fileno()

	# gets the tty attributes
	originalAttributes = termios.tcgetattr(unit)
	newAttributes = termios.tcgetattr(unit)
	# SETTING IFLAGS
	# IXON disabls software flow controls like ctrl s and ctrl q
	# thats a legacy feature apparently
	# ICRNL stops enter from returning a newline
	# BRKINT stops ctrl c and other break characters but they should
	# already have been turned off already lol
	# INPCK is somehting about parity checking which should not affect
	# modern terminals
	# ISTRIP stops the 8th byte form being removed before returning
	# probably already disabled by default but hey why not
	newAttributes[0] &= ~(
		termios.IXON | termios.ICRNL | termios.BRKINT | termios.INPCK |\
		termios.ISTRIP
	)
	# SETTING OFLAGS
	# OPOST disables the post proccess of adding a carrige return to a newline
	# note this means we need to specifically input a \r to go back to the start
	# of a line now since the cursor only moves down automatically with OPOST off
	newAttributes[1] &= ~(
		termios.OPOST
	)
	# SETTING CFLAGS
	# CS8 sets 8 bytes per bit which should be default
	newAttributes[2] |= ~(
		termios.CS8
	)
	# SETTING LFLAGS
	# ECHO turn off echoing back the char we just typed
	# ICANON turns off canonical mode to raw mode
	# ISIG disables ctrl c and ctrl z
	newAttributes[3] &= ~(
		termios.ECHO | termios.ICANON |termios.ISIG | termios.IEXTEN
	)
	# SETTING VTIME AND VMIN
	# VMIN sets the minimum amount of bytes to be read before return
	# at 0 it returns as soon as it receives an input
	newAttributes[6][termios.VMIN] = 0
	# VTIME sets the wait time for reading inputs as a number over 10 of a second
	# so at 1 its 1/10 of a second before it moves on to the next line of code
	newAttributes[6][termios.VTIME] = 1

	# sets the new tty attributesw
	termios.tcsetattr(unit, termios.TCSAFLUSH, newAttributes)

	# gets terminal width/height in characters
	# NOTE ioctl does not work on all systems but fuck that im not
	# doing the hard way with escape sequences \\:
	# i really do be chasing modules huh
	terminfo = ioctl(unit, termios.TIOCGWINSZ, pack("HHHH", 0,0,0,0))
	# a tupe containing: (rows, columns, x pixels, y pixels)
	# dont need pixels tho
	terminfo = unpack("HHHH", terminfo)
	heightChar = terminfo[0]
	widthChar = terminfo[1]
	prevWidth = terminfo[0]
	prevHeight = terminfo[1]

	resize = True

	# declare sum more stuff
	cursorx = 0
	cursory = 1
	cursorlastx = 1
	cursorlasty = 1

	# marks
	markexists = False
	markx1 = -1
	marky1 = -1
	markx2 = -1
	marky2 = -1

	# buffer list
	buf = []

	# canvas
	frames = [clearCanvas(widthChar, heightChar, " ")]
	frame = 0

	# save last character
	lastchar = ""

	# cutbuffer
	clip = [[]]

	# command interface
	terminal = False
	terminalframe = clearCanvas(widthChar, heightChar, " ")

	# time stuff
	previousdt = time()

	# playback
	playing = False
	direction = 1
	framerate = 24

	# for the windows users
	os.system("")

	# main program loop
	while True:

		# reget window size
		# still breaks currently lol \\:
		# even in 1.4 it is still busted
		if resize:
			terminfo = ioctl(unit, termios.TIOCGWINSZ, pack("HHHH", 0,0,0,0))
			terminfo = unpack("HHHH", terminfo)
			heightChar = terminfo[0]
			widthChar = terminfo[1]
			if heightChar != prevHeight or widthChar != prevWidth:
				prevWidth = terminfo[0]
				prevHeight = terminfo[1]
				frames = resizeAnimation(frames, widthChar, heightChar)

		# get time since last update
		dt = time() - previousdt
		previousdt = time()

		# cursor limits
		cursorxmin = 0
		cursorxmax = widthChar-1
		cursorymin = 1
		cursorymax = heightChar-1

		# reads at least 1 byte from the standard input
		# we need to read 4 bytes to account for shift and ctrl shift keys
		rawchar = os.read(unit, 4)
		# keeps rawchar in case i need to debug with it
		char = handleInput(rawchar)

		# double tap inputs
		# exit condition(s)
		if char == "^Q" and lastchar == "^Q":
			break
		# remove frame
		elif char == "^H" and lastchar == "^H" and not terminal:
			if len(frames) > 1: frames.pop(frame)
		# append frame
		elif char == "^\\" and lastchar == "^\\" and not terminal:
			frames.append(clearCanvas(widthChar, heightChar, " "))
		# insert frame
		elif char == "^J" and lastchar == "^J" and not terminal:
			frames.insert(frame, clearCanvas(widthChar, heightChar, " "))
		elif char == "^K" and lastchar == "^K" and not terminal:
			if len(frames)-1 == frame:
				frames.append(clearCanvas(widthChar, heightChar, " "))
			else:
				frames.insert(frame+1,
				clearCanvas(widthChar, heightChar, " "))
			frame += 1
		# duplicate frame
		elif char == "L" and lastchar == "^L" and not terminal:
			frames.insert(frame, frames[frame])
			frame += 1

		# save char input
		if char: lastchar = char

		# single tap controls
		# move cursor vertically
		if char == "UPARROW":
			cursory -= 1
		elif char == "DOWNARROW":
			cursory += 1
		# move cursor horizontally
		elif char == "RIGHTARROW":
			cursorx += 1
		elif char == "LEFTARROW":
			cursorx -= 1
		# offset vertical
		elif char == "CTRLSHIFTUPARROW":
			cursory -= 1
			cursorx -= 1
		elif char == "CTRLSHIFTDOWNARROW":
			cursory += 1
			cursorx -= 1
		# offset horizontal
		elif char == "CTRLSHIFTRIGHTARROW":
			cursory += 1
			cursorx -= 2
		elif char == "CTRLSHIFTLEFTARROW":
			cursory -= 1
			cursorx -= 2
		# fast movement
		elif char == "SHIFTUPARROW":
			cursory -= 4
		elif char == "SHIFTDOWNARROW":
			cursory += 4
		elif char == "SHIFTRIGHTARROW":
			cursorx += 4
		elif char == "SHIFTLEFTARROW":
			cursorx -= 4
		# tab
		elif char == "^I":
			cursorx += 4
		# jump to borders
		elif char == "^Z":
			cursorx = cursorxmin
		elif char == "^V":
			cursorx = cursorxmax
		elif char == "^X":
			cursory = cursorymin
		elif char == "^C":
			cursory = cursorymax
		# center cursor
		elif char == "^B":
			cursorx = cursorxmax//2
		elif char == "^N":
			cursory = cursorymax//2
		# frame change
		elif char == "^[" and not terminal:
			frame -= 1
		elif char == "^]" and not terminal:
			frame += 1
		# toggle playbackmode / edit mode
		elif char == "^S" and not terminal:
			if playing:
				playing = False
				# use os.read as frame limiter
				newAttributes[6][termios.VTIME] = 1
				termios.tcsetattr(unit, termios.TCSAFLUSH, newAttributes)
			elif not playing:
				playing = True
				# use framerate a limiter
				newAttributes[6][termios.VTIME] = 0
				termios.tcsetattr(unit, termios.TCSAFLUSH, newAttributes)
		# jump to start / end frames
		elif char == "^A" and not terminal:
			frame = 0
		elif char == "^D" and not terminal:
			frame = len(frames)-1
		# switch to edit mode / terminal mode
		elif char == "^F":
			if terminal:
				terminal = False
				cursorx = cursorlastx
				cursory = cursorlasty
			elif not terminal:
				terminal = True
				cursorlastx = cursorx
				cursorlasty = cursory
				cursorx = 0
				cursory = 1
			playing = False
		# run command
		# should move this into a function
		elif char == "^G":
			if terminal:
				command = "".join(terminalframe[cursory-1])
				command = command.split(" ")
				try:
					if command[0].lower() == "save":
						command.insert(1, frames)
						saveAnimation(command)
						terminalframe = printToCanvas(terminalframe,
							cursorx, cursory, f"Saved {command[2]}.")
					elif command[0].lower() == "load":
						loaded = loadAnimation(command)
						loaded = resizeAnimation(loaded, widthChar, heightChar)
						frames = loaded
						frame = 0
						terminalframe = printToCanvas(terminalframe,
							cursorx, cursory, f"Loaded {command[1]}.")
					elif command[0].lower() == "help":
						terminalframe = printToCanvas(terminalframe,
							cursorx, cursory, "Read the README!")
					elif command[0].lower() == "playback":
						if not command[1] or command[1] == " ":
							framerate = 24
						else:
							framerate = command[1]
						if not command[2] or command[2] == " ":
							direction = 1
						else:
							direction = command[2]
						terminalframe = printToCanvas(terminalframe,
							cursorx, cursory, "Playback settings updated!")
					elif command[0].lower() == "execute":
						exec("".join(command[1:]))
						terminalframe = printToCanvas(terminalframe,
							cursorx, cursory, "Done.")
				except Exception as exc:
					terminalframe = printToCanvas(terminalframe,
						cursorx, cursory, str(exc))
		# set marks
		elif char == "^@":
			if markexists:
				markx2 = cursorx
				marky2 = cursory
				markexists = False
			else:
				markx1 = cursorx
				marky1 = cursory
				markexists = True
		# copy
		elif char == "^O":
			if markx1 > -1 and marky1 > -1 and markx2 > -1 and marky2 > -1:
				clip = getFromCanvas(frames[frame], markx1, marky1-1, markx2,
					marky2-1)
			markx1 = -1
			marky1 = -1
			markx2 = -1
			marky2 = -1
		# cut
		elif char == "^_":
			if markx1 > -1 and marky1 > -1 and markx2 > -1 and marky2 > -1:
				clip = getFromCanvas(frames[frame], markx1, marky1-1, markx2,
					marky2-1)
				cut = clearCanvas(len(clip[0]), len(clip), fillchar=" ")
				frames[frame] = drawToCanvas(frames[frame], markx1, marky1-1,
					cut)
			markx1 = -1
			marky1 = -1
			markx2 = -1
			marky2 = -1
		# paste
		elif char == "^P":
			frames[frame] = drawToCanvas(frames[frame], cursorx, cursory-1,
			clip)
		# drawing tools
		# draw line
		elif char == "^W":
			if markx1 > -1 and marky1 > -1 and markx2 > -1 and marky2 > -1:
				fill = frames[frame][cursory-1][cursorx]
				frames[frame] = drawLine(frames[frame], markx1, marky1-1,
					markx2, marky2-1, fillchar=fill)
				markx1 = -1
				marky1 = -1
				markx2 = -1
				marky2 = -1
		# draw bezier curve
		elif char == "^Y":
			if markx1 > -1 and marky1 > -1 and markx2 > -1 and marky2 > -1:
				fill = frames[frame][cursory-1][cursorx]
				frames[frame] = drawCurve(frames[frame], markx1, marky1-1,
				markx2, marky2-1, cursorx, cursory-1, t=1, fillchar=fill)
				markx1 = -1
				marky1 = -1
				markx2 = -1
				marky2 = -1
		# draw a hollow rectangle
		elif char == "^R":
			if markx1 > -1 and marky1 > -1 and markx2 > -1 and marky2 > -1:
				fill = frames[frame][cursory-1][cursorx]
				frames[frame] = drawBox(frames[frame], markx1, marky1-1,
				markx2, marky2-1, fillchar=fill)
				markx1 = -1
				marky1 = -1
				markx2 = -1
				marky2 = -1
		# draw triangle
		elif char == "^T":
			if markx1 > -1 and marky1 > -1 and markx2 > -1 and marky2 > -1:
				fill = frames[frame][cursory-1][cursorx]
				frames[frame] = drawTriangle(frames[frame], markx1, marky1-1,
				markx2, marky2-1, cursorx, cursory-1, fillchar=fill)
				markx1 = -1
				marky1 = -1
				markx2 = -1
				marky2 = -1
		# draw elipses
		elif char == "^E":
			if markx1 > -1 and marky1 > -1 and markx2 > -1 and marky2 > -1:
				fill = frames[frame][cursory-1][cursorx]
				frames[frame] = drawElipse2(frames[frame], markx1, marky1-1,
				markx2, marky2-1, cursorx, cursory-1, fillchar=fill)
				markx1 = -1
				marky1 = -1
				markx2 = -1
				marky2 = -1
		# backspace
		elif char == "^?" and not playing:
			if terminal:
				terminalframe[cursory-1][cursorx-1] = " "
			elif not terminal:
				frames[frame][cursory-1][cursorx-1] = " "
			if cursorx == cursorxmin: cursory -= 1
			cursorx -= 1
		# enter
		elif char == "^M" and not playing:
			cursory += 1
			cursorx = 0
		# draw if nothing else
		elif len(char) == 1 and not playing:
			if terminal:
				terminalframe[cursory-1][cursorx] = char[0]
			elif not terminal:
				frames[frame][cursory-1][cursorx] = char[0]
			cursorx += 1

		# not even sure if this is needed since only shift arrowkeys and tab
		# move more than 1 at a time
		# clamp cursor position within screen bounds
		if cursory < cursorymin-1:
			cursory = cursorymin
		elif cursory > cursorymax+1:
			cursory = cursorymax
		elif cursorx < cursorxmin-1:
			cursorx = cursorxmin
		elif cursorx > cursorxmax+1:
			cursorx = cursorxmax

		# wraparound at screen edge
		if cursory == cursorymin-1:
			cursory = cursorymax
		elif cursory == cursorymax+1:
			cursory = cursorymin
		if cursorx == cursorxmin-1:
			cursorx = cursorxmax
		elif cursorx == cursorxmax+1:
			cursorx = cursorxmin

		# playback
		if playing: frame += direction

		# frame move wrap
		if frame < 0:
			frame = len(frames) - 1
		elif frame > len(frames) - 1:
			frame = 0

		# empty buffer
		buf = clearCanvas(widthChar, heightChar, fillchar=" ")

		# draw title bar
		if terminal:
			editmode = "command"
		elif playing:
			editmode = "playback"
		else:
			editmode = "edit"

		titlechar = lastchar
		if len(lastchar) > 1: titlechar = lastchar.lower()

		if markx1 < 0 and marky1 < 0:
			titlecx1 = "x"
			titlecy1 = "y"
		else:
			titlecx1 = str(markx1)
			titlecy1 = str(marky1)

		if markx2 < 0 and marky2 < 0:
			titlecx2 = "x"
			titlecy2 = "y"
		else:
			titlecx2 = str(markx2)
			titlecy2 = str(marky2)

		# overcomplicated title bar
		title = "@[catscii v" + str(version) + "][mode " +\
		editmode + "][frame " + str(frame+1) + "/" + str(len(frames)) +\
		"][cursor " + str(cursorx+1) + ":" + str(cursory) +\
		"][marks " + titlecx1 + ":" + titlecy1  + "|" +\
		titlecx2 + ":" + titlecy2 +\
		"][" + titlechar + "]"

		title += "=" * (widthChar-len(title))

		buf = printToCanvas(buf, 0, 0, title, widthChar)

		# draw contents
		if terminal:
			buf = drawToCanvas(buf, 0, 1, terminalframe)
		else:
			buf = drawToCanvas(buf, 0, 1, frames[frame])

		# draw cursor
		if not playing:	buf = drawCursor(buf, cursorx, cursory)

		# draw marks
		if markx1 > -1 and marky1 > -1: buf = drawCursor(buf, markx1, marky1,
			blink=True)
		if markx2 > -1 and marky2 > -1: buf = drawCursor(buf, markx2, marky2,
			blink=True)


# OLD
		# draw to screen
#		if terminal:
#			buf = drawBuffer(buf,
#				cursorx, cursory,
#				char, lastchar,
#				terminalframe, "X", "X",
#				widthChar, heightChar, title="COMMAND MODE")
#		elif not terminal:
#			buf = drawBuffer(buf,
#				cursorx, cursory,
#				char, lastchar,
#				frames[frame], frame+1, len(frames),
#				widthChar, heightChar, title="EDITING")

		# draw the whole buffer
		drawScreen(unit, buf)

		# cap framerate
		if playing:
			delay = 0 if 1/framerate - dt < 0 else 1/framerate - dt
			sleep(delay)

#except Exception as exc:
#	print(exc)
finally:
	# clear the screen one last time
	# and show cursor again!!!
	os.write(unit, b"\033[0m\033[2J\033[?25h")
	# reset terminal back to original attributes
	termios.tcsetattr(unit, termios.TCSAFLUSH, originalAttributes)
	print("Bye bye!")

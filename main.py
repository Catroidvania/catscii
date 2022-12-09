# a kwik n dirty ascii animation program
# made with catroidvania
# first created 2 12 22
# verison 1.3
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


def handleInput(key):
	# seperates regualr keys from control keys etc
	# and turns keypresses inso strings
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
	if key == b"\x00": return "^@"	#
	if key == b"\x01": return "^A"	# jump to first frame
	if key == b"\x02": return "^B"	# center cursor horizontally
	if key == b"\x03": return "^C"	# cursor to bottom edge
	if key == b"\x04": return "^D"	# jump to last frame
	if key == b"\x05": return "^E"	# execute terminal mode command
	if key == b"\x06": return "^F"	#
	if key == b"\x07": return "^G"	# bell
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
	if key == b"\x12": return "^R"	#
	if key == b"\x13": return "^S"	# toggle playback mode
	if key == b"\x14": return "^T"	# toggle terminal mode
	if key == b"\x15": return "^U"	# set mark 2
	if key == b"\x16": return "^V"	# cursor to right edge
	if key == b"\x17": return "^W"	#
	if key == b"\x18": return "^X"	# cursor to top edge
	if key == b"\x19": return "^Y"	# set mark 1
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
	version = 1.3

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

	resize = True

	# declare sum more stuff
	cursorx = 0
	cursory = 1
	cursorlastx = 1
	cursorlasty = 1

	# marks
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

	# savig / loading

	# random stuff
	decorchar = ":"
	#choice(["!", "@", "#", "$", "%", "&", "=", ":"])

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
		if resize:
			terminfo = ioctl(unit, termios.TIOCGWINSZ, pack("HHHH", 0,0,0,0))
			terminfo = unpack("HHHH", terminfo)
			heightChar = terminfo[0]
			widthChar = terminfo[1]

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
		elif char == "SHIFTUPARROW":
			cursory -= 1
			cursorx -= 1
		elif char == "SHIFTDOWNARROW":
			cursory += 1
			cursorx -= 1
		# offset horizontal
		elif char == "SHIFTRIGHTARROW":
			cursory += 1
			cursorx -= 2
		elif char == "SHIFTLEFTARROW":
			cursory -= 1
			cursorx -= 2
		# fast movement
		elif char == "CTRLSHIFTUPARROW":
			cursory -= 4
		elif char == "CTRLSHIFTDOWNARROW":
			cursory += 4
		elif char == "CTRLSHIFTRIGHTARROW":
			cursorx += 4
		elif char == "CTRLSHIFTLEFTARROW":
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
		elif char == "^T":
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
		elif char == "^E":
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
		elif char == "^Y":
			markx1 = cursorx
			marky1 = cursory
		elif char == "^U":
			markx2 = cursorx
			marky2 = cursory
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

		# overcomplicated title bar
		title = "%[catscii v" + str(version) + "]=[" +\
		editmode + "]=[frame " + str(frame+1) + "/" + str(len(frames)) +\
		"]=[cursor " + str(cursorx+1) + ":" + str(cursory) +\
		"]=[" + titlechar + "]" #[" + str(round(dt, 4)) + "]"
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
			delay = 1/framerate if 1/framerate - dt < 0 else 1/framerate - dt
			sleep(delay)

#except Exception as exc:
#	print(exc)
finally:
	# clear the screen one last time
	# and show cursor again!!!
	os.write(unit, b"\033[2J\033[?25h")
	# reset terminal back to original attributes
	termios.tcsetattr(unit, termios.TCSAFLUSH, originalAttributes)
	print("Bye bye!")

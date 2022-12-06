# a kwik n dirty ascii animation program
# made with catroidvania
# first created 2 12 22
# verison 1.1

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
from time import time_ns, sleep
# random (:
from random import choice


def drawBuffer(buf, cx, cy, key, lastkey, contents, frame, framecount,
	width=80, height=24, title="CATSCII"):

	# creates the buffer to be returned
	for row in range(height+1):
		# skip the clear screen codes
		if not row: continue
		# adds a clearline to the start
		buf[row].insert(0, "\033[K")
		if row == 1:
			# titlebar

			# some info
			title = "{ " + title +\
				 " | " + str(cx) + ":" + str(cy-2) +\
				 " | " + str(frame) + "/" + str(framecount) + " }"

			# center align
			buf[row][1:] = " " * ((width-len(title))//2) +\
				 title +\
				 " " * ((width-len(title))//2)

			# keypressed
		elif row == 2:
			title = "[ " + lastkey + " ]"
			buf[row][0:] = "=" * ((width-len(title))//2) + title +\
				"=" * ((width-len(title))//2)
		elif row == height:
			buf[row] = "=" * width
		else:
# dont need line numbers
#			num = str(row-2)
			# some border decor
#			if len(num) < 2:
#				buf[row][1:3] = num + " " * (2 - len(num))
#			elif len(num) > 2:
#				buf[row][1:3] = num[-2:]
#			else:
#				buf[row][1:3] = num
#			buf[row][3] = "|"
			buf[row][1] = "["

			# contents
			buf[row][2:] = contents[row-2]

		# draw cursor
		if row == cy: buf[row][cx]= "\033[7m"+contents[row-2][cx]+"\033[0m"

		# moves everything down unless its the last row
		if row < height - 1: buf[row].append("\r\n")
	return buf


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
			canvas[row + y][x:] = content[row][:canvasWidth-x]
		else:
			canvas[row + y][x:] = content[row]

	return canvas


def printToCanvas(canvas, x, y, string, canvasWidth=None):
	# print a string to the canvas

	# if none are supplied
	if not canvasWidth: canvasWidth = len(canvas[0])-1

	# write to buffer row

	# so we dont draw off the edge
	if len(string) > canvasWidth:
		canvas[y][x:] = string[:canvasWidth-x]
	else:
		canvas[y][x:] = string

	return canvas


def drawCursor(canvas, x, y):
	# draws the cursor as inverted text
	canvas[y][x] = "\033[7m" + canvas[y][x] + "\033[0m"

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
	if key == b"\x00": return "^@"	# null
	if key == b"\x01": return "^A"	#
	if key == b"\x02": return "^B"	# center cursor horizontally
	if key == b"\x03": return "^C"	# cursor to bottom edge
	if key == b"\x04": return "^D"	#
	if key == b"\x05": return "^E"	# execute terminal mode command
	if key == b"\x06": return "^F"	#
	if key == b"\x07": return "^G"	# bell
	# backspace doesnt seem to send hex 08 though
	if key == b"\x08": return "^H"	# delete frame
	if key == b"\x09": return "^I"	# tab
	if key == b"\x0A": return "^J"	# insert frame left
	if key == b"\x0B": return "^K"	# insert frame right
	if key == b"\x0C": return "^L"	# duplicat frame
	if key == b"\x0D": return "^M"	# enter
	if key == b"\x0E": return "^N"	# center cursor vertically
	if key == b"\x0F": return "^O"	#
	if key == b"\x10": return "^P"	#
	if key == b"\x11": return "^Q"	# quit program without saving
	if key == b"\x12": return "^R"	#
	if key == b"\x13": return "^S"	#
	if key == b"\x14": return "^T"	# toggle terminal mode
	if key == b"\x15": return "^U"	#
	if key == b"\x16": return "^V"	# cursor to right edge
	if key == b"\x17": return "^W"	#
	if key == b"\x18": return "^X"	# cursor to top edge
	if key == b"\x19": return "^Y"	#
	if key == b"\x1A": return "^Z"	# cursor to left edge
	if key == b"\x1B": return "^["	# change frame left
	if key == b"\x1C": return "^\\"	# append frame
	if key == b"\x1D": return "^]"	# change frame right
	if key == b"\x1E": return "^^"	#
	if key == b"\x1F": return "^_"	#
	# this works instead
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


def saveAnimation(frames, filename=None, width=80, height=24, linesep="@@"):
	# saving an animation
	if not filename: filename = "untitled" + str(time_ns()) + ".txt"
	width = int(width)
	height = int(height)

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


def loadAnimation(filename, linesep="@@"):
	# load an animation
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

	# version inso
	version = 1.1

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

	# buffer list
	buf = []

	# canvas
	frames = [clearCanvas(widthChar, heightChar, " ")]
	frame = 0

	# save last character
	lastchar = ""

	# command interface
	terminal = False
	terminalframe = clearCanvas(widthChar, heightChar, " ")

	# savig / loading

	# random stuff
	decorchar = "::"
	#choice(["!", "@", "#", "$", "%", "&", "=", ":"])

	# main program loop
	while True:

		# reget window size
		if resize:
			terminfo = ioctl(unit, termios.TIOCGWINSZ, pack("HHHH", 0,0,0,0))
			terminfo = unpack("HHHH", terminfo)
			heightChar = terminfo[0]
			widthChar = terminfo[1]

		# cursor limits
		cursorxmin = 0
		cursorxmax = widthChar-1
		cursorymin = 1
		cursorymax = heightChar-1

		# reads at least 1 byte from the standard input
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
			frame -= 1
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
		# since height is always one row short for some reason
		elif char == "DOWNARROW":
			cursory += 1
		# move cursor horizontally
		elif char == "RIGHTARROW":
			cursorx += 1
		elif char == "LEFTARROW":
			cursorx -= 1
		# find where the empty string is coming from
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
		# backspace
		elif char == "^?":
			if terminal:
				terminalframe[cursory-1][cursorx-1] = " "
			elif not terminal:
				frames[frame][cursory-1][cursorx-1] = " "
			if cursorx == 1: cursory -= 1
			cursorx -= 1
		# enter
		elif char == "^M":
			cursory += 1
			cursorx = 0
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
		# run command
		# should move this into a function
		elif char == "^E":
			if terminal:
				command = "".join(terminalframe[cursory-1])
				command = command.split(" ")
				try:
					if command[0].lower() == "save":
						saveAnimation(
						frames, command[1], command[2], command[3], command[4])
						terminalframe[cursory][0:]= "Saved "+ command[1]+ "!"
					elif command[0].lower() == "load":
						loaded = loadAnimation(command[1], command[2])
						loaded = resizeAnimation(loaded, widthChar, heightChar)
						frames = loaded
						terminalframe[cursory][0:]= "Loaded "+ command[1]+"!"
					elif command[0].lower() == "help":
						terminalframe[cursory][0:]= "Not implemented yet lol!"
				except Exception as exc:
					terminalframe[cursory][0:] = str(exc)
		# draw if nothing else
		elif len(char) == 1:
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

		# frame move wrap
		if frame < 0:
			frame = len(frames) - 1
		elif frame > len(frames) - 1:
			frame = 0

		# empty buffer
		buf = clearCanvas(widthChar, heightChar, fillchar=" ")

		# draw title bar
		if terminal:
			editmode = "COMMAND MODE"
		else:
			editmode = "EDIT MODE"

		title = decorchar + "[ CATSCII v" + str(version) + " ][ " +\
		editmode + " ][ FRAME " + str(frame+1) + "/" + str(len(frames)) +\
		" ][ CURSOR " + str(cursorx+1) + ":" + str(cursory) +\
		" ][ " + lastchar + " ]"
		title += "=" * (widthChar-len(title))
		buf = printToCanvas(buf, 0, 0, title, widthChar)

		# draw contents
		if terminal:
			buf = drawToCanvas(buf, 0, 1, terminalframe)
		else:
			buf = drawToCanvas(buf, 0, 1, frames[frame])

		# draw cursor
		buf = drawCursor(buf, cursorx, cursory)

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

#except Exception as exc:
#	print(exc)
finally:
	# clear the screen one last time
	# and show cursor again!!!
	os.write(unit, b"\033[2J\033[?25h")
	# reset terminal back to original attributes
	termios.tcsetattr(unit, termios.TCSAFLUSH, originalAttributes)
	print("Bye bye!")

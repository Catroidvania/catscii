# a kwik n dirty ascii animation program
# made with catroidvania
# first created 2 12 22
# verison 1.0

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
from time import time_ns

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


def clearBuffer(buf, width=80, height=24, fillchar=" "):
	# does well, clearing buffer stuff
	buf = [[fillchar for col in range(width)] for row in range(height)]

	# clear screen and move cursor to top left for drawing
	buf.insert(0, "\033[?25l\033[H")

	return buf


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
				 " | " + str(cx-4) + ":" + str(cy-2) +\
				 " | " + str(frame) + "/" + str(framecount) + " }"

			# center align
			buf[row][1:] = " " * ((width-len(title))//2) +\
				 title +\
				 " " * ((width-len(title))//2)

			# keypressed
		elif row == 2:
			title = "[ " + lastkey + " ]"
			buf[row][:] = "=" * ((width-len(title))//2) + title +\
				"=" * ((width-len(title))//2)
		elif row == height:
			buf[row] = "=" * width
		else:
			num = str(row-2)
			# some border decor
			if len(num) < 2:
				buf[row][1:3] = num + " " * (2 - len(num))
			elif len(num) > 2:
				buf[row][1:3] = num[-2:]
			else:
				buf[row][1:3] = num
			buf[row][3] = "|"

			# contents
			buf[row][4:] = contents[row-2]

		# draw cursor
		if row == cy+1: buf[row][cx]= "\033[7m"+contents[row-2][cx-4]+"\033[0m"

		# moves everything down unless its the last row
		if row < height - 1: buf[row].append("\r\n")
	return buf


def drawScreen(unitno, buf):
	# draws the buffer to screen
	try:
		stringbuf = ""
		for row in buf:
			stringbuf += "".join(row)

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
		[" " for col in range(width-3)] for row in range(height-1)]
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
			if f == 0: continue
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


try:
	# move the variable stuff up top into here???
	# sets the new tty attributesw
	termios.tcsetattr(unit, termios.TCSAFLUSH, newAttributes)

	# gets some terminal info
	# NOTE ioctl does not work on all systems but fuck that im not
	# doing the hard way with escape sequences \\:
	# i really do be chasing modules huh
	terminfo = ioctl(unit, termios.TIOCGWINSZ, pack("HHHH", 0,0,0,0))
	# a tupe containing: (rows, columns, xpixels, ypixels)
	# we really dont need the pixel sizes but hey why not
	terminfo = unpack("HHHH", terminfo)
	heightChar = terminfo[0]
	widthChar = terminfo[1]

	# declare sum more stuff
	cursorx = 0
	cursory = 0
	cursorlastx = 0
	cursorlasty = 0

	# buffer list
	buf = []

	# canvas
	frames = [[
		[" " for col in range(widthChar-3)] for row in range(heightChar-1)]]
	frame = 0

	# save last character
	lastchar = ""

	# command interface
	terminal = False
	terminalframe = [
		[" " for col in range(widthChar-3)] for row in range(heightChar-1)]

	# savig / loading

	# main program loop
	while True:
		# reads one byte from the standard input
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
			frames.append([
						[" " for col in range(widthChar-4)]
							for row in range(heightChar-1)])
		# insert frame
		elif char == "^J" and lastchar == "^J" and not terminal:
			frames.insert(0 if frame == 0 else frame-1, [
						[" " for col in range(widthChar-4)]
							for row in range(heightChar-1)])
			frame -= 1
		elif char == "^K" and lastchar == "^K" and not terminal:
			frames.insert(-1 if frame == len(frames)-1 else frame+1, [
						[" " for col in range(widthChar-4)]
							for row in range(heightChar-1)])
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
		# tab
		elif char == "^I":
			cursorx += 4
		# backspace
		elif char == "^?":
			if terminal:
				terminalframe[cursory-1][cursorx-5] = " "
			elif not terminal:
				frames[frame][cursory-1][cursorx-5] = " "
			if cursorx == 1: cursory -= 1
			cursorx -= 1
		# enter
		elif char == "^M":
			cursory += 1
			cursorx = 0
		# jump to borders
		elif char == "^Z":
			cursorx = 0
		elif char == "^V":
			cursorx = widthChar
		elif char == "^X":
			cursory = 0
		elif char == "^C":
			cursory = heightChar
		# center cursor
		elif char == "^B":
			cursorx = widthChar//2
		elif char == "^N":
			cursory = heightChar//2
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
				cursory = 0
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
		# hotkeys
		# todo
		# draw if nothing else
		elif len(char) == 1:
			if terminal:
				terminalframe[cursory-1][cursorx-4] = char[0]
			elif not terminal:
				frames[frame][cursory-1][cursorx-4] = char[0]
			cursorx += 1

		# clamp cursor position within screen bounds
		if cursory < 1: cursory = 2
		if cursory > heightChar - 1: cursory = heightChar - 2
		if cursorx > widthChar + 1: cursorx = widthChar
		if cursorx < 3: cursorx = 4

		# wraparound at screen edge
		if cursory == 1:
			cursory = heightChar - 2
		elif cursory == heightChar - 1:
			cursory = 2
		if cursorx == widthChar + 1:
			cursorx = 4
		elif cursorx == 3:
			cursorx = widthChar

		# frame move wrap
		if frame < 0:
			frame = len(frames) - 1
		elif frame > len(frames) - 1:
			frame = 0

		# empty buffer
		buf = clearBuffer(buf, widthChar, heightChar, fillchar=" ")

		# draw to screen
		if terminal:
			buf = drawBuffer(buf,
				cursorx, cursory,
				char, lastchar,
				terminalframe, "X", "X",
				widthChar, heightChar, title="COMMAND MODE")
		elif not terminal:
			buf = drawBuffer(buf,
				cursorx, cursory,
				char, lastchar,
				frames[frame], frame+1, len(frames),
				widthChar, heightChar, title="EDITING")

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

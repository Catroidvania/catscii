# catscii

a terminal based ascii animation editor i made for fun

made by catroidvania with actually terrible python code

## usage

just run main.py from the terminal with

`python3 main.py`

to view animations use the included viewer

(have yet to put a builtin watch feature into the main program lol)

(ill do it eventually i promiisssee)

`python3 viewer.py`

then fill in the prompts

filename: the animation file (should be .txt or whatever you saved it as)

frame separator: a string that separates frames (@@ by default)

framerate: playback speed in frames per second (techincally bugged atm)

looping: how many times to loop the animation

to quit just give it blank filename

### controls

arrow keys: up down left right movement of the cursor


shift up: moves up and back

shift down: moves down and back

shift left: moves up and twice back

shift right: moves down and twice back

#### ctrl keys

^b: center cursor horizontally

^n: center cursor vertically


^z: jump cursor to left edge

^x: jump cursor to top edge

^c: jump cursor to bottom edge

^v: jump cursor to right edge

^[: go to previous frame

^]: go to next frame

^e: execute command

^t: toggle command mode / edit mode

### double tap ctrl keys

^q: quit without saving


^\: append frame

^h: delete current frame

^j: insert new frame left

^k: insert new frame right

^l: duplicate current frame

### command mode

enter / exit commande mode with the toggle command mode key (default ^t)

in the command mode you can type out a command on a line and press

the execute command key (default ^e) to run it

#### commands

save; filename width(default 80) height(default 24) linesep(default @@)

load; filename linesep(default @@)

## other stuff

yeah theres gonna be more added if i care to work on this project lol

might happen:

-- builtin playback

-- command hotkeys

-- copy/cut/paste

-- not terrible code (yeah like thatll ever happen)

-- onionskin??

-- colors (might just save that for a version 2.0)

-- bold/italics/underline etc (might also be saved for a 2.0)

-- mouse support (hmmmmmmmmmmmmmmm)

-- tba

## in other words

fork this repo and make a better one lol

catroidvania out

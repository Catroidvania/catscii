# catscii v1.3

a terminal based ascii animation editor i made for fun

made by catroidvania with actually terrible python code

## usage

just run main.py from the terminal with

`python3 main.py`


### controls

arrow keys: up down left right movement of the cursor


shift up: moves up and back

shift down: moves down and back

shift left: moves up and twice back

shift right: moves down and twice back


ctrl shift up: moves up but faster

ctrl shift down: moves down but faster

ctrl shift left: moves left but faster

ctrl shift right: moves right but faster


#### ctrl keys

^b: center cursor horizontally

^n: center cursor vertically


^z: jump cursor to left edge

^x: jump cursor to top edge

^c: jump cursor to bottom edge

^v: jump cursor to right edge


^y: set first mark

^u: set second mark

^o: copy marked content

^_: cut marked content

^p: paste at cursor


^[: go to previous frame

^]: go to next frame

^s: toggle playback made / edit mode

^a: jump to first frame

^d: jump to last frame


^e: execute command

^t: toggle command mode / edit mode

### double tap ctrl keys

^q: quit without saving


^\\: append frame

^h: delete current fram

^j: insert new frame left

^k: insert new frame right

^l: duplicate current frame

### copy cut paste

as of version 1.3 we have copy, cut and paste!

set the first and second marks to specify a region of text (marks will flash)

note that the while the first and second marks should be at the top left and

bottom right corner, it works in any order but may not include the row

or column the mark itself is on

use their respective hotkeys as seen above to either cut or copy the text

between the set marks

use the paste key to paste the cut/copied content to the cursor location

note that whitespace still gets copied (may be changed in the future)

### command mode

enter / exit commande mode with the toggle command mode key (default ^t)

in the command mode you can type out a command on a line and press

the execute command key (default ^e) to run it

all parameters need to be filled out for it to work correctly

(itll be changed evetually but its not high on the list of priorities)

#### commands

save; filename width(default 80) height(default 24) linesep(default @@)

load; filename linesep(default @@)

playback; framerate(default 24) direction(default 1, -1 for backwards etc)

help; tba

### playback

pressing the toggle playback key plays the animation based on the framerate

which you can set with the playback command

## other stuff

yeah theres gonna be more added if i care to work on this project lol

might happen:

-- command hotkeys

-- line / curve / box; draw primatives

-- config file

-- not terrible code (yeah like thatll ever happen)

-- onionskin??

-- colors (might just save that for a version 2.0)

-- bold/italics/underline etc (might also be saved for a 2.0)

-- mouse support (hmmmmmmmmmmmmmmm)

-- tba

## in other words

fork this repo and make a better one lol

have fun gamers

catroidvania out

# animation veiwer program for veiwscii

from time import sleep


def getFromFile(file, linesep="@@"):
	with open(file, "r") as file:
		frames = []
		frame = []
		while True:
			line = file.readline()
			if not line: break
			if line[-1] == "\n": line = line[:-1]
			if line == linesep:
				frames.append(frame)
				frame = []
			else:
				frame.append(line)

	return frames


def playFrames(frames, framerate=12, width=None, height=None, newline=True):
	framerate = 1 / framerate
	if not width: width = len(frames[0][0])
	if not height: height = len(frames[0])
	for frame in frames:
		print("\033[0J")
		for line in frame:
			print(line)
		print(f"\033[{height+2}A")
		sleep(framerate)
	if newline: print(f"\033[{height}B")


while __name__ == "__main__":
	try:
		toplay = input("Play what animation?: ")
		if not toplay: break
		sep = input("Frame separator?: ")
		if not sep: sep = "@@"
		fps = int(input("Framerate?: "))
		if not fps: fps = 12
		loop = int(input("Loop how many times?: "))
		if not loop: loop = 1
		anim = getFromFile(toplay, linesep=sep)

		for r in range(loop):
			playFrames(anim, framerate=fps, newline=loop-1)

		print(f"Finished playing {toplay}!")

	except Exception as exc:
		print(exc)

print("Bye bye!")

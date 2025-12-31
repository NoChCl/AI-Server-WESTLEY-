import pickle, os


def unpackList(l):
	
	for thing in l:
		if isinstance(thing, list): unpackList(thing)
		else: print(thing)

pkl_files = []

# Walk through the directory
for filename in os.listdir("./"):
    if filename.endswith(".pkl"):
        pkl_files.append(filename)
        print(str(len(pkl_files))+": "+filename)

fileIndex = int(input("\nEnter the file number of the pkl file you would like to read: "))-1

messages=pickle.load(open(pkl_files[fileIndex],"rb"))

unpackList(messages)

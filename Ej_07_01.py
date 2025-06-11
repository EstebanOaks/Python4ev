

fname = input("Enter file name: ")
fh = open(fname)

for line in fh:
    ly=line.rstrip
    print(line.upper())
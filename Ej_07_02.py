

fname = input("Enter file name: ")
fh = open(fname)
count=0
total=0
for line in fh:
    
    if not line.startswith("X-DSPAM-Confidence:"):
        continue
    posnum= line.find(":")
    flo = float(line[posnum+1:].strip())
    total=total+flo
    count=count+1

prom=total/count
    
print("Average spam confidence:",prom)
import re 

name = input("enter file:")
handle = open(name)
numlist=list()

for line in handle:
    line=line.rstrip()
    busca = re.findall("[0-9]+",line)
    if not busca : 
        continue
    for num in busca:
        numlist.append(int(num))


print(sum(numlist))

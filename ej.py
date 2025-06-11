name = input("Enter file:")
if len(name) < 1:
    name = "mbox-short.txt"
handle = open(name)


count=dict()

for line in handle:
    pal= line.split()
    if not line.startswith("From:"):
         continue
    
    for word in pal:
        if word in count:
            count[word] = count.get(word[1],0)+1

print(count)
       
        
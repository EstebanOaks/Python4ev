import json
import urllib.request


url = input("Ingrese URL - ")

datos = urllib.request.urlopen(url).read()


info = json.loads(datos)


print(json.dumps(info, indent=4)) 

suma = 0
for item in info['comments']:
    suma  = suma+item['count']

print("Suma total de 'count':", suma)

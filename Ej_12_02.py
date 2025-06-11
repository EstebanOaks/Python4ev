import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl


ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


url = input('Enter - ')
parte = int(input("Seleccione qué link quiere abrir: "))
veces = int(input("¿Cuántas veces desea realizar esta acción?: "))


for i in range(veces):
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup('a')

    count = 0
    for tag in tags:
        count += 1
        if count == parte:
            link = tag.get('href', None)
            print("Abriendo:", link)
            url = link  
            break
print(url)
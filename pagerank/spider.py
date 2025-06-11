import sqlite3
import ssl
import urllib.request
import urllib.parse
import urllib.error
from bs4 import BeautifulSoup
import re

# Crear contexto SSL sin verificación
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Conexión a la base de datos
conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

# Crear tablas
cur.execute('''
CREATE TABLE IF NOT EXISTS Pages 
(id INTEGER PRIMARY KEY, url TEXT UNIQUE, html TEXT, error INTEGER, old_rank REAL, new_rank REAL)''')

cur.execute('''
CREATE TABLE IF NOT EXISTS Links (from_id INTEGER, to_id INTEGER)''')

cur.execute('''
CREATE TABLE IF NOT EXISTS Webs (url TEXT UNIQUE)''')

# Pedir URL
starturl = input('Enter web url or enter: ')
if len(starturl) < 1:
    starturl = 'http://books.toscrape.com/'

# Procesar la URL base
if starturl.endswith('/'):
    starturl = starturl[:-1]
web = starturl
if starturl.endswith('.htm') or starturl.endswith('.html'):
    pos = starturl.rfind('/')
    web = starturl[:pos]

# Agregar sitio a Webs y Pages
if len(web) > 1:
    cur.execute('INSERT OR IGNORE INTO Webs (url) VALUES (?)', (web,))
    cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES (?, NULL, 1.0)', (starturl,))
    conn.commit()

# Cuántas páginas descargar
many = int(input('How many pages: '))
count = 0

while count < many:
    cur.execute('SELECT id, url FROM Pages WHERE html IS NULL AND error IS NULL ORDER BY RANDOM() LIMIT 1')
    row = cur.fetchone()
    if row is None:
        print('No unretrieved HTML pages found')
        break

    id, url = row
    print(f"{count + 1} {url}", end=' ')

    # Solo trabajar dentro de los sitios permitidos
    cur.execute('SELECT url FROM Webs')
    webs = [row[0] for row in cur.fetchall()]
    if not any(url.startswith(web) for web in webs):
        print("URL fuera de dominio")
        cur.execute('DELETE FROM Pages WHERE id=?', (id,))
        conn.commit()
        continue

    try:
        # Agregar user-agent para evitar bloqueos
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, context=ctx)
        html = response.read()
        if response.getcode() != 200:
            print("Error on page", response.getcode())
            cur.execute('UPDATE Pages SET error=? WHERE url=?', (response.getcode(), url))
            conn.commit()
            continue
    except Exception as e:
        print("Unable to retrieve or parse page", e)
        cur.execute('UPDATE Pages SET error=-1 WHERE url=?', (url,))
        conn.commit()
        continue

    soup = BeautifulSoup(html, 'html.parser')
    tags = soup('a')
    print(f"({len(tags)} links)")

    cur.execute('UPDATE Pages SET html=? WHERE url=?', (memoryview(html), url))
    conn.commit()

    for tag in tags:
        href = tag.get('href', None)
        if href is None: continue
        href = urllib.parse.urljoin(url, href)
        pos = href.find('#')
        if pos > 1:
            href = href[:pos]
        if href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif'):
            continue
        if href.endswith('/'):
            href = href[:-1]

        if not any(href.startswith(web) for web in webs):
            continue

        cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES (?, NULL, 1.0)', (href,))
        conn.commit()

        cur.execute('SELECT id FROM Pages WHERE url=? LIMIT 1', (href,))
        row = cur.fetchone()
        if row is None:
            continue
        toid = row[0]
        cur.execute('INSERT INTO Links (from_id, to_id) VALUES (?, ?)', (id, toid))

    count += 1

conn.commit()

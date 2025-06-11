import sqlite3

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

# Recuperar páginas
cur.execute('SELECT id, new_rank FROM Pages')
pages = cur.fetchall()

# Configurar número de iteraciones
sval = input('How many iterations:')
if len(sval) < 1:
    sval = 1
else:
    sval = int(sval)

for i in range(sval):
    print(f"\nIteration {i+1}")
    next_ranks = dict()
    total = 0.0
    for (id, new_rank) in pages:
        next_ranks[id] = 0.0
        total += new_rank

    for (id, old_rank) in pages:
        giving_ids = list()
        cur.execute('SELECT to_id FROM Links WHERE from_id=?', (id,))
        for row in cur:
            giving_ids.append(row[0])
        if len(giving_ids) < 1:
            continue
        amount = old_rank / len(giving_ids)
        for to_id in giving_ids:
            next_ranks[to_id] += amount

    new_total = 0.0
    for id in next_ranks:
        new_total += next_ranks[id]

    # Normalización
    evap = (total - new_total) / len(next_ranks)
    for id in next_ranks:
        next_ranks[id] += evap

    # Guardar nuevos valores
    for id in next_ranks:
        cur.execute('UPDATE Pages SET old_rank=new_rank, new_rank=? WHERE id=?', (next_ranks[id], id))
    conn.commit()

cur.close()

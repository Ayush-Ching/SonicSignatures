import sqlite3

# conn = sqlite3.connect("database/fingerprints.db")
# cursor = conn.cursor()

# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(cursor.fetchall())

# conn.close()



# conn = sqlite3.connect("database/fingerprints.db")
# cursor = conn.cursor()

# cursor.execute("SELECT * FROM songs")
# print(cursor.fetchall())

# cursor.execute("SELECT COUNT(*) FROM fingerprints")
# print(cursor.fetchone())

# conn.close()



# conn = sqlite3.connect("database/fingerprints.db")
# cursor = conn.cursor()

# cursor.execute("PRAGMA table_info(fingerprints)")
# print(cursor.fetchall())

# conn.close()



conn = sqlite3.connect("database/single.db")
cur = conn.cursor()

print(cur.execute("PRAGMA table_info(fingerprints);").fetchall())
print(cur.execute("PRAGMA table_info(songs);").fetchall())

conn.close()
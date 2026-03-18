import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        number TEXT PRIMARY KEY,
        count INTEGER
    )
    """)

    conn.commit()
    conn.close()

def report_number(number):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports WHERE number=?", (number,))
    result = cursor.fetchone()

    if result:
        cursor.execute("UPDATE reports SET count = count + 1 WHERE number=?", (number,))
    else:
        cursor.execute("INSERT INTO reports (number, count) VALUES (?, 1)", (number,))

    conn.commit()
    conn.close()
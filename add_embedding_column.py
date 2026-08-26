import sqlite3

from app.core.config import DATABASE_PATH


connection = sqlite3.connect(DATABASE_PATH)

cursor = connection.cursor()

try:
    cursor.execute(
        """
        ALTER TABLE chunks
        ADD COLUMN embedding TEXT
        """
    )

    connection.commit()

    print("Embedding kolonu basariyla eklendi.")

except sqlite3.OperationalError as error:

    if "duplicate column name" in str(error).lower():
        print("Embedding kolonu zaten mevcut.")
    else:
        print(f"Database islemi: {error}")

finally:
    connection.close()
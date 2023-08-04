import bcrypt
import psycopg2

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

db_params = {
    'host': 'localhost',
    'port': 5432,
    'database': 'workout'
}

username = 'jrh'
bio = 'lover of everything'
password = 'hannah'

hashed_password = hash_password(password)

conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

try:
    insert_query = "INSERT INTO users (username, bio, password_digest) VALUES (%s, %s, %s);"
    cursor.execute(insert_query, (username, bio, hashed_password))
    conn.commit()
    print("User seeded successfully!")
except (psycopg2.Error, psycopg2.DatabaseError) as error:
    print("Error seeding user:", error)
finally: 
    cursor.close()
    conn.close()
from flask import *
import psycopg2

app = Flask(__name__)
conn = psycopg2.connect#(database=db_CEPBMOON,
                        #user=DB_USER,
                        #password=DB_PASS,
                        #host=DB_HOST,
                        #port=DB_PORT)
cursor = conn.cursor()

@app.get("/lista")
def listar():
    cursor.execute("""
SELECT 


""")
    
@app.post("/")
def publicar(str):
    cursor.execute(str)
    cursor.commit()
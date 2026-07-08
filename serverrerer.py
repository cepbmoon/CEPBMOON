from flask import *
import psycopg2

app = Flask(__name__)
conn = psycopg2.connect(database="db_CEPBMOON",
                        user="avnadmin",
                        host="cepbmoon-cepb-moon.c.aivencloud.com",
                        port=27526,
                        sslmode="require")
cursor = conn.cursor()
cursor.execute("SHOW TABLES;")
print(cursor.fetchall())

@app.get("/fila_delegaciones")
def obtener_botones():

    cursor.execute("""
        SELECT texto
        FROM botones
        WHERE sesion_id = %s
    """, (...))

    return [...]

@app.get("/historial_intervenciones")

@app.get("/historial_")


@app.post("/")
def publicar(str):
    cursor.execute(str)
    cursor.commit()
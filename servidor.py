from flask import *
import mysql.connector

conn = mysql.connector.connect(database="db_CEPBMOON",
                        user="avnadmin",
                        host="cepbmoon-cepb-moon.c.aivencloud.com",
                        password="AVNS_tHX9YWtgYm64fJwHvSo",
                        port=27526)
cursor = conn.cursor(dictionary=True)

app = Flask(__name__)

@app.get("/GETdelegaciones")
def getDelegaciones():
    cursor.execute("SELECT nomDelegacion FROM tabDelegaciones")
    return cursor.fetchall()

@app.post("/POSTfila_delegaciones")
def postFila():
    datos = request.json
    delegacion = datos["delegacion"]
    cursor.execute("SELECT idDelegacion FROM tabDelegaciones WHERE nomDelegacion=%s",(delegacion,))
    cursor.execute("INSERT INTO tabFila(idDelegacion) VALUES(%s)",(cursor.fetchone()["idDelegacion"],))
    conn.commit()

    return {"ok": True}

@app.get("/GETfila_delegaciones")
def getFila():
    cursor.execute("""SELECT tabDelegaciones.nomDelegacion FROM tabDelegaciones INNER JOIN tabFila ON tabDelegaciones.idDelegacion = tabFila.idDelegacion ORDER BY tabFila.idFila""")
    return cursor.fetchall()

if __name__ == "__main__":
    app.run(debug= True)

# def obtener_botones():

#     cursor.execute("""
#         SELECT texto
#         FROM botones
#         WHERE sesion_id = %s
#     """, (...))

#     return [...]

# @app.get("/historial_intervenciones")

# @app.get("/historial_")


# @app.post("/")
# def publicar(str):
#     cursor.execute(str)
#     cursor.commit()
from flask import *
import mysql.connector

conn = mysql.connector.connect(database="db_CEPBMOON",
                        user="avnadmin",
                        host="cepbmoon-cepb-moon.c.aivencloud.com",
                        password="AVNS_tHX9YWtgYm64fJwHvSo",
                        port=27526)

app = Flask(__name__)

## implementar un sistema de una variable "Cambios" y una ruta "Estados"
## tengo que actualizar que cada POST modifique una tabla tabCambios, cambie la variable Cambios a 

@app.get("/GETpasar_codigo")
def getPasarCodigo():
    cursor = conn.cursor(dictionary=True)
    codigo = request.json["codigo"]
    try:
        params = request.json["params"]
    except:
        params = 0
    if params:
        cursor.execute(codigo, tuple(params))
    else:
        cursor.execute(codigo)
    return cursor.fetchall()
    cursor.close()

@app.post("/POSTpasar_codigo")
def postPasarCodigo():
    cursor = conn.cursor(dictionary=True)
    codigo = request.json["codigo"]
    try:
        params = request.json["params"]
    except:
        params = 0
    if params:
        cursor.execute(codigo, tuple(params))
    else:
        cursor.execute(codigo)
    conn.commit()
    cursor.close()

@app.post("/POSTfila_delegaciones")
def postFila():
    cursor = conn.cursor(dictionary=True)
    datos = request.json
    delegacion = datos["delegacion"]
    cursor.execute("SELECT idDelegacion FROM tabDelegaciones WHERE nomDelegacion=%s",(delegacion,))
    cursor.execute("INSERT INTO tabFila(idDelegacion) VALUES(%s)",(cursor.fetchone()["idDelegacion"],))
    conn.commit()

    return {"ok": True}
    cursor.close()

@app.get("/GETfila_delegaciones")
def getFila():
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT tabDelegaciones.nomDelegacion FROM tabDelegaciones INNER JOIN tabFila ON tabDelegaciones.idDelegacion = tabFila.idDelegacion ORDER BY tabFila.idFila""")
    return cursor.fetchall()
    cursor.close()

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
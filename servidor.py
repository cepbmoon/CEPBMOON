from flask import *
import pymysql

conn = pymysql.connect(
    host="cepbmoon-cepb-moon.c.aivencloud.com",
    port=27526,
    user="avnadmin",
    password="AVNS_tHX9YWtgYm64fJwHvSo",
    database="db_CEPBMOON",
    cursorclass=pymysql.cursors.DictCursor
)

app = Flask(__name__)

## implementar un sistema de una variable "Cambios" y una ruta "Estados"
## tengo que actualizar que cada POST modifique una tabla tabCambios, cambie la variable Cambios a 

@app.get("/GETpasar_codigo")
def getPasarCodigo():
    cursor = conn.cursor()
    codigo = request.json["codigo"]
    try:
        params = request.json["params"]
    except:
        params = 0
    if params:
        cursor.execute(codigo, tuple(params))
    else:
        cursor.execute(codigo)
    respuesta = cursor.fetchall()
    cursor.close()
    return jsonify(respuesta)

@app.post("/POSTpasar_codigo")
def postPasarCodigo():
    cursor = conn.cursor()
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
    return {"ok": True}

@app.route("/cambios")
def cambios():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabCambios")
    cambios = cursor.fetchall()
    cursor.execute("UPDATE tabCambios SET hayCambios = 0, fila = 0, historial = 0;")
    conn.commit()
    cursor.close()
    return jsonify(cambios)

@app.post("/POSTfila_delegaciones")
def postFila():
    cursor = conn.cursor()
    datos = request.json
    delegacion = datos["delegacion"]
    cursor.execute("SELECT idDelegacion FROM tabDelegaciones WHERE nomDelegacion=%s",(delegacion,))
    cursor.execute("INSERT INTO tabFila(idDelegacion) VALUES(%s)",(cursor.fetchone()["idDelegacion"],))
    conn.commit()

    cursor.close()
    return {"ok": True}

@app.get("/GETfila_delegaciones")
def getFila():
    cursor = conn.cursor()
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
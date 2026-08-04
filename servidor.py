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

@app.get("/cambios/verCambios")
def verCambios():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabCambios")
    cambios = cursor.fetchall()
    cursor.close()
    return jsonify(cambios)

@app.post("/cambios/cambiarFila")
def cambiarFila():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabCambios;")
    versiones = cursor.fetchall()
    cursor.execute(f"UPDATE tabCambios SET versionCambios = {int(versiones[0]["versionCambios"]) + 1}, versionFila = {int(versiones[0]["versionFila"]) + 1};")
    return {"ok": True}

@app.post("/cambios/cambiarHistorial")
def cambiarHistorial():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabCambios;")
    versiones = cursor.fetchall()
    cursor.execute(f"UPDATE tabCambios SET versionCambios = {int(versiones[0]["versionCambios"]) + 1}, versionHistorial = {int(versiones[0]["versionHistorial"]) + 1};")
    return {"ok": True}

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
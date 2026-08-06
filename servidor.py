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

class conectarMesa():
    @app.get("/GETingresarForo")
    def ingresarForo():
        cursor = conn.cursor()
        params = request.json["params"]
        cursor.execute("SELECT idSesion FROM tabSesiones WHERE nomForo = %s AND contraseña = %s", (params["nomForo"], params["contraseña"])) #Revisa si hay el foro y contraseña
        foro = cursor.fetchone()
        if foro:
            return {"idSesion":foro["idSesion"]}      # Hay todo ouuu yeeeaaaa
        else:
            cursor.execute("SELECT idSesion FROM tabSesiones WHERE nomForo = %s;", (params["nomForo"],))
            nom = cursor.fetchall()
            if nom:                        # La contraseña está equivocada
                return {"error":"Contraseña equivocada"}
                                    # No existe el foro
            return {"error":"No se encuentra el foro"}

    @app.get("/POSTcrearForo")
    def crearForo():
        cursor = conn.cursor()
        params = request.json["params"]
        cursor.execute("SELECT nomForo FROM tabSesiones WHERE nomForo = %s", (params["nomForo"],))
        foro_yaexiste = cursor.fetchall()
        if foro_yaexiste:
            return {"error": "Foro ya existente"}
        else:
            cursor.execute("INSERT INTO tabSesiones(nomForo, contraseña) VALUES(%s,%s);", (params["nomForo"], params["contraseña"],))
            conn.commit()
            cursor.execute("SELECT idSesion FROM tabSesiones WHERE nomForo = %s", (params["nomForo"],))
            return {"idSesion": cursor.fetchone()["idSesion"]}

class mainpy():
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
        sesion = request.json["idSesion"]
        cursor.execute(f"SELECT * FROM tabCambios WHERE idSesion = {sesion};")
        cambios = cursor.fetchall()
        cursor.close() 
        return jsonify(cambios)

    @app.post("/cambios/cambiarFila")
    def cambiarFila():
        cursor = conn.cursor()
        sesion = request.json["idSesion"]
        cursor.execute(f"SELECT * FROM tabCambios WHERE idSesion = {sesion};")
        versiones = cursor.fetchall()
        cursor.execute(f"UPDATE tabCambios SET versionCambios = {int(versiones[0]["versionCambios"]) + 1}, versionFila = {int(versiones[0]["versionFila"]) + 1} WHERE idSesion = {sesion};")
        return {"ok": True}

    @app.post("/cambios/cambiarHistorial")
    def cambiarHistorial():
        cursor = conn.cursor()
        sesion = request.json["idSesion"]
        cursor.execute(f"SELECT * FROM tabCambios WHERE idSesion = {sesion};")
        versiones = cursor.fetchall()
        cursor.execute(f"UPDATE tabCambios SET versionCambios = {int(versiones[0]["versionCambios"]) + 1}, versionHistorial = {int(versiones[0]["versionHistorial"]) + 1} WHERE idSesion = {sesion};")
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
        cursor.close()
        return cursor.fetchall()

if __name__ == "__main__":
    app.run(debug= True)
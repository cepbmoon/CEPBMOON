from flask import *
import pymysql
from pymysqlpool.pool import Pool
import asyncio
from flask_socketio import SocketIO, send, emit, join_room, leave_room

pool = Pool(host="cepbmoon-cepb-moon.c.aivencloud.com",
    port=27526,
    user="avnadmin",
    password="AVNS_tHX9YWtgYm64fJwHvSo",
    database="db_CEPBMOON",
    cursorclass=pymysql.cursors.DictCursor,
    )

conn = pool.get_conn()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class conectarMesa():
    @app.get("/GETingresarForo")
    def ingresarForo():
        conexion = pool.get_conn()
        cursor = conexion.cursor()
        params = request.json["params"]
        cursor.execute("SELECT idSesion FROM tabSesiones WHERE nomForo = %s AND contraseña = %s", (params["nomForo"], params["contraseña"])) #Revisa si hay el foro y contraseña
        foro = cursor.fetchone()
        if foro:
            pool.release(conexion)
            return {"idSesion":foro["idSesion"]}      # Hay todo ouuu yeeeaaaa
        else:
            cursor.execute("SELECT idSesion FROM tabSesiones WHERE nomForo = %s;", (params["nomForo"],))
            nom = cursor.fetchall()
            if nom:                        # La contraseña está equivocada
                return {"error": "Contraseña equivocada"}
                                    # No existe el foro
            return {"error": "No se encuentra el foro"}

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
            sesion = cursor.fetchone()["idSesion"]
            cursor.execute("INSERT INTO tabCambios(idSesion, versionCambios, versionFila, versionHistorial) VALUES(%s, 0, 0, 0)", (sesion,))
            cursor.execute("INSERT INTO tabTiempos(idSesion, leer, cuestionar, pensar, contestar) VALUES(%s, 60, 30, 30, 60)", (sesion,))
            cursor.execute("INSERT INTO tabMesa(idSesion) VALUES(%s)", (sesion,))
            conn.commit()
            return {"idSesion": sesion}

class nombrarMesa():
    @app.get("/GETmesa")
    def getMesa():
        cursor = conn.cursor()
        params = request.json["idSesion"]
        cursor.execute("SELECT * FROM tabMesa WHERE idSesion = %s", (params))
        mesa = cursor.fetchone()
        cursor.close()
        return mesa

    @app.post("/POSTmesa")
    def postMesa():
        cursor = conn.cursor()
        presidente, moderador, secretario, evaluador, ano = request.json["params"]
        sesion = request.json["idSesion"]
        cursor.execute(f"UPDATE tabMesa SET Presidente= %s, Moderador= %s, Secretario= %s, Evaluador= %s, Año = %s WHERE idSesion = %s", (presidente, moderador, secretario, evaluador, ano, sesion,))
        conn.commit()
        return {"ok": True}


class mainpy():
    @socketio.on("unirse_sesion")
    def unirse_sesion(data):
        sesion = data["idSesion"]
        join_room(str(sesion))

    @app.get("/GETdelegaciones")
    def getDelegaciones():
        cursor = conn.cursor()
        cursor.execute("SELECT nomDelegacion FROM tabDelegaciones")
        delegaciones = cursor.fetchall()
        cursor.close()
        return delegaciones

    @app.get("/GETidDelegacion")
    def getidDelegacion():
        cursor = conn.cursor()
        delegacion = request.json["delegacion"]
        cursor.execute("SELECT idDelegacion FROM tabDelegaciones WHERE nomDelegacion = %s", (delegacion))
        idDelegacion = cursor.fetchall()
        cursor.close()
        return idDelegacion

    @socketio.on("cambiarFila")
    def cambiarFila(data):
        print(data)
        conexion = pool.get_conn()
        cursor = conexion.cursor()
        sesion = data["idSesion"]

        if "delegacion" in data:
            delegacion = data["delegacion"]
            cursor.execute("SELECT idDelegacion FROM tabDelegaciones WHERE nomDelegacion = %s", (delegacion))
            idDelegacion = cursor.fetchall()
            cursor.close()
            cursor.execute("delete from tabFila where idDelegacion=%s;", (idDelegacion,))
            conexion.commit()

        cursor.execute("SELECT versionCambios, versionFila, versionHistorial FROM tabCambios WHERE idSesion = %s", (sesion,))
        versiones = cursor.fetchone()

        versionCambios = int(versiones["versionCambios"]) + 1
        versionFila = int(versiones["versionFila"]) + 1
        versionHistorial = int(versiones["versionHistorial"])

        cursor.execute("UPDATE tabCambios SET versionCambios = %s, versionFila = %s WHERE idSesion = %s""", (versionCambios, versionFila, sesion))
        conexion.commit()

        cursor.execute("""SELECT tabDelegaciones.nomDelegacion FROM tabDelegaciones
                        INNER JOIN tabFila ON tabDelegaciones.idDelegacion = tabFila.idDelegacion
                        WHERE tabFila.idSesion = %s
                        ORDER BY tabFila.idFila""", (sesion,))
        fila = cursor.fetchall()
        cursor.close()
        pool.release(conexion)

        socketio.emit("cambios",{
            "fila": fila,
            "versionCambios": versionCambios,
            "versionFila": versionFila,
            "versionHistorial": versionHistorial
            }, room=str(sesion))
        
        return {"ok": True}

    @app.post("/cambios/cambiarHistorial")
    def cambiarHistorial():
        conexion = pool.get_conn()
        cursor = conexion.cursor()
        sesion = request.json["idSesion"]
        cursor.execute("SELECT versionCambios, versionFila, versionHistorial FROM tabCambios WHERE idSesion = %s", (sesion,))
        versiones = cursor.fetchone()

        versionCambios = int(versiones["versionCambios"]) + 1
        versionFila = int(versiones["versionFila"]) 
        versionHistorial = int(versiones["versionHistorial"]) + 1

        cursor.execute("UPDATE tabCambios SET versionCambios = %s, versionHistorial = %s WHERE idSesion = %s""", (versionCambios, versionHistorial, sesion))

        cursor.execute("""SELECT tabDelegaciones.nomDelegacion, tabHistorial.turnos FROM tabDelegaciones
                    INNER JOIN tabHistorial ON tabDelegaciones.idDelegacion = tabHistorial.idDelegacion 
                    WHERE tabHistorial.idSesion = %s
                    ORDER BY tabHistorial.idHistorial""", (sesion,))
        historial = cursor.fetchall()
        conn.commit()
        cursor.close()
        pool.release(conexion)
        socketio.emit("cambios",{
                        "historial": historial,
                        "versionCambios": versionCambios,
                        "versionFila": versionFila,
                        "versionHistorial": versionHistorial
                      },room=str(sesion))
        return {"ok": True}

    @socketio.on("POSTfila_delegaciones")             # Fila de delegaciones
    def postFila(data):
        conexion = pool.get_conn()
        cursor = conexion.cursor()
        delegacion = data["delegacion"]
        sesion = data["idSesion"]
        cursor.execute("SELECT idDelegacion FROM tabDelegaciones WHERE nomDelegacion=%s",(delegacion,))
        cursor.execute("INSERT INTO tabFila(idDelegacion, idSesion) VALUES(%s, %s)",(cursor.fetchone()["idDelegacion"], sesion,))
        conexion.commit()
        cursor.close()
        
        pool.release(conexion)
        return {"ok": True}

    @app.get("/GETfila_delegaciones")
    def getFila():
        cursor = conn.cursor()
        sesion = request.json["idSesion"]
        cursor.execute("""SELECT tabDelegaciones.nomDelegacion FROM tabDelegaciones
                        INNER JOIN tabFila ON tabDelegaciones.idDelegacion = tabFila.idDelegacion
                        WHERE tabFila.idSesion = %s
                        ORDER BY tabFila.idFila""", (sesion,))
        fila = cursor.fetchall()
        cursor.close()
        return jsonify(fila)

    @app.post("/limpiarFila")
    def limpiarFila():
        cursor = conn.cursor()
        sesion = request.json["idSesion"]
        cursor.execute("delete from tabFila WHERE idSesion = %s", (sesion,))
        conn.commit()
        cursor.close()
        return {"ok": True}

    @app.post("/POSThistorial_delegaciones")        # Historial de delegaciones
    def postHistorial():
        conexion = pool.get_conn()
        cursor = conexion.cursor()
        sesion = request.json["idSesion"]
        nomDelegacion = request.json["nomDelegacion"]
        cursor.execute("""SELECT tabHistorial.turnos FROM tabHistorial 
                        INNER JOIN tabDelegaciones ON tabHistorial.idDelegacion = tabDelegaciones.idDelegacion 
                        WHERE tabDelegaciones.nomDelegacion = %s;""", (nomDelegacion,))
        turnos = cursor.fetchall()
        if turnos:
            turnos = turnos[-1]["turnos"]
        else:
            turnos = 0

        cursor.execute("""INSERT INTO tabHistorial (idDelegacion, turnos, idSesion)
                        SELECT idDelegacion, %s, %s FROM tabDelegaciones 
                        WHERE tabDelegaciones.nomDelegacion = %s""", ((turnos+1), sesion, nomDelegacion,))
        conexion.commit()
        cursor.close()
        pool.release(conexion)
        return {"ok": True}
    
    @app.get("/GEThistorial")
    def getHistorial():
        cursor = conn.cursor()
        sesion = request.json["idSesion"]
        cursor.execute("""SELECT tabDelegaciones.nomDelegacion, tabHistorial.turnos FROM tabDelegaciones
                    INNER JOIN tabHistorial ON tabDelegaciones.idDelegacion = tabHistorial.idDelegacion 
                    WHERE tabHistorial.idSesion = %s
                    ORDER BY tabHistorial.idHistorial""", (sesion,))
        cursor.close()
        return jsonify(cursor.fetchall())

    @app.post("/POSTtiempos")
    def postTiempos():
        cursor = conn.cursor()
        columna = request.json["columna"]
        segundos = request.json["segundos"]
        sesion = request.json["idSesion"]
        cursor.execute("UPDATE tabTiempos SET %s = %s WHERE idSesion = %s", (columna, segundos, sesion))
        conn.commit()
        return {"ok": True}

    @app.get("/GETtiempos")
    def getTiempos():
        cursor = conn.cursor()
        sesion = request.json["idSesion"]
        cursor.execute("SELECT leer, cuestionar, pensar, contestar FROM tabTiempos WHERE idSesion = %s", (sesion,))
        tiempos = cursor.fetchone()
        cursor.close()
        return jsonify(tiempos) 

    @app.post("/cronometrarDelegacion")
    def CronometrarDelegacion(dataCronDele):
        pass

    @app.post("/POSTobservacion")
    def postObservacion():
        cursor = conn.cursor()
        params = request.json["params"]
        sesion = request.json["idSesion"]
        cursor.execute("""INSERT INTO tabPuntaje (idDelegado, idSesion, idObs, descObs, puntaje)
				            SELECT idDelegado, %s, %s, %s, %s
				            FROM tabDelegados
				            WHERE tabDelegados.nomDelegado = %s""", (sesion, params[0], params[1], params[2], params[3]))
        return {"ok": True}

    @app.get("/GETobservaciones")
    def getObservaciones():
        cursor = conn.cursor()
        sesion = request.json["idSesion"]
        cursor.execute("""SELECT tabDelegaciones.nomDelegacion, tabDelegados.nomDelegado, tabPuntaje.descObs, tabPuntaje.puntaje FROM tabPuntaje
                        INNER JOIN tabDelegados ON tabDelegados.idDelegado = tabPuntaje.idDelegado
                        INNER JOIN tabDelegaciones ON tabDelegaciones.idDelegacion = tabDelegados.idDelegacion WHERE tabPuntaje.idSesion = %s
                        ORDER BY nomDelegacion DESC""", (sesion,))
        observaciones = cursor.fetchall()
        cursor.close()
        if observaciones:
            return observaciones
        else:
            return {"ok": True}

    @app.post("/POSTdelegados")
    def postDelegados():
        cursor = conn.cursor()
        sesion = request.json["idSesion"]
        delegacion = request.json["delegacion"]
        cursor.execute("""UPDATE tabDelegaciones SET idSesion = %s WHERE nomDelegacion = %s""", (sesion, delegacion))
        conn.commit()
        cursor.execute("""INSERT INTO tabDelegados
                            (nomDelegado, idDelegacion, alumnoCEPB, idCursoSeccion)
                            SELECT NULL, tabDelegaciones.idDelegacion, NULL, NULL
                            FROM tabDelegaciones
                            WHERE tabDelegaciones.nomDelegacion = %s
                            AND NOT EXISTS (
                                SELECT *
                                FROM tabDelegados
                                WHERE tabDelegaciones.idDelegacion = tabDelegados.idDelegacion)

                            UNION ALL

                            SELECT NULL, tabDelegaciones.idDelegacion, NULL, NULL
                            FROM tabDelegaciones
                            WHERE tabDelegaciones.nomDelegacion = %s
                            AND NOT EXISTS (
                                SELECT *
                                FROM tabDelegados
                                WHERE tabDelegados.idDelegacion = tabDelegaciones.idDelegacion);""", (delegacion, ))
        conn.commit()
        return {"ok": True}

    @app.get("/GETdelegados")
    def getDelegados():
        cursor = conn.cursor()
        delegacion = request.json["delegacion"]
        cursor.execute("""SELECT nomDelegado FROM tabDelegados 
                        INNER JOIN tabDelegaciones 
                        ON tabDelegados.idDelegacion = tabDelegaciones.idDelegacion 
                        WHERE tabDelegaciones.nomDelegacion = %s;""", (delegacion,))

        delegados = cursor.fetchall()
        cursor.close()
        return delegados

if __name__ == "__main__":
    socketio.run(app, debug=True)
print("\33c")
import os
import pymysql
from flask import *
from dotenv import load_dotenv
from pymysqlpool import ConnectionPool
from flask_socketio import SocketIO, send, emit, join_room, leave_room

load_dotenv()

config = {'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),  # Your password is now safe
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
         "cursorclass":pymysql.cursors.DictCursor
    }

pool = ConnectionPool(size=10, maxsize=20, **config)

conn = pool.get_connection() 

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def inicio():
    return "Servidor CEPBMOON funcionando correctamente"

class conectarMesa():
    @app.get("/GETingresarForo")
    def ingresarForo():
        conexion = pool.get_connection()
        cursor = conexion.cursor()
        params = request.json["params"]
        cursor.execute("SELECT idSesion FROM tabSesiones WHERE nomForo = %s AND contraseña = %s", (params["nomForo"], params["contraseña"])) #Revisa si hay el foro y contraseña
        foro = cursor.fetchone()
        if foro:
            conexion.close()
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
        connexion_GETdelegaciones = pool.get_connection()
        try:
            cursor = connexion_GETdelegaciones.cursor()
            try:
                sesion = request.json["idSesion"]
                cursor.execute("SELECT * FROM tabDelegaciones WHERE idSesion = %s", (sesion,))
            except:
                cursor.execute("SELECT * FROM tabDelegaciones")
            delegaciones = cursor.fetchall()
            return delegaciones
        finally:
            connexion_GETdelegaciones.close()

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
        conexion_cambiar_fila = pool.get_connection()
        try:
            cursor = conexion_cambiar_fila.cursor()
            sesion = data["idSesion"]

            if "delegacion" in data:
                delegacion = data["delegacion"]

                cursor.execute("SELECT idDelegacion FROM tabDelegaciones WHERE nomDelegacion = %s", (delegacion))
                idDelegacion = cursor.fetchall()[0]["idDelegacion"]
                cursor.execute("delete from tabFila where idDelegacion=%s;", (idDelegacion,))
                conexion_cambiar_fila.commit()

            cursor.execute("SELECT versionCambios, versionFila, versionHistorial FROM tabCambios WHERE idSesion = %s", (sesion,))
            versiones = cursor.fetchone()

            versionCambios = int(versiones["versionCambios"]) + 1
            versionFila = int(versiones["versionFila"]) + 1
            versionHistorial = int(versiones["versionHistorial"])

            cursor.execute("UPDATE tabCambios SET versionCambios = %s, versionFila = %s WHERE idSesion = %s""", (versionCambios, versionFila, sesion))
            conexion_cambiar_fila.commit()

            cursor.execute("""SELECT tabDelegaciones.nomDelegacion FROM tabDelegaciones
                            INNER JOIN tabFila ON tabDelegaciones.idDelegacion = tabFila.idDelegacion
                            WHERE tabFila.idSesion = %s
                            ORDER BY tabFila.idFila""", (sesion,))
            fila = cursor.fetchall()

            socketio.emit("cambios",{
                "fila": fila,
                "versionCambios": versionCambios,
                "versionFila": versionFila,
                "versionHistorial": versionHistorial
                }, room=str(sesion))
            
            return {"ok": True}
        finally:
            conexion_cambiar_fila.close()

    @socketio.on("cambiarHistorial")
    def cambiarHistorial(data):
        conexion_historial = pool.get_connection()
        try:
            cursor = conexion_historial.cursor()
            sesion = data["idSesion"]
            cursor.execute("SELECT versionCambios, versionFila, versionHistorial FROM tabCambios WHERE idSesion = %s", (sesion,))
            versiones = cursor.fetchone()

            versionCambios = int(versiones["versionCambios"]) + 1
            versionFila = int(versiones["versionFila"]) 
            versionHistorial = int(versiones["versionHistorial"]) + 1

            cursor.execute("UPDATE tabCambios SET versionCambios = %s, versionHistorial = %s WHERE idSesion = %s""", (versionCambios, versionHistorial, sesion))
            conexion_historial.commit()

            cursor.execute("""SELECT tabDelegaciones.nomDelegacion, tabHistorial.turnos FROM tabDelegaciones
                        INNER JOIN tabHistorial ON tabDelegaciones.idDelegacion = tabHistorial.idDelegacion 
                        WHERE tabHistorial.idSesion = %s
                        ORDER BY tabHistorial.idHistorial""", (sesion,))
            historial = cursor.fetchall()

            socketio.emit("cambios",{
                            "historial": historial,
                            "versionCambios": versionCambios,
                            "versionFila": versionFila,
                            "versionHistorial": versionHistorial
                        },room=str(sesion))
            return {"ok": True}
        finally:
            conexion_historial.close()

    @socketio.on("POSTfila_delegaciones")             # Fila de delegaciones
    def postFila(data):
        con_local = pool.get_connection()
        try:
            cursor = con_local.cursor()
            delegacion = data["delegacion"]
            sesion = data["idSesion"]
            cursor.execute("SELECT idDelegacion FROM tabDelegaciones WHERE nomDelegacion=%s",(delegacion,))
            cursor.execute("INSERT INTO tabFila(idDelegacion, idSesion) VALUES(%s, %s)",(cursor.fetchone()["idDelegacion"], sesion,))
            con_local.commit()
        finally:
            con_local.close() 

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
        conexion_historial_delegaciones = pool.get_connection()
        try:
            cursor = conexion_historial_delegaciones.cursor()
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
            conexion_historial_delegaciones.commit()
            return {"ok": True}
        finally:
            conexion_historial_delegaciones.close()
    
    @app.get("/GEThistorial")
    def getHistorial():
        cursor = conn.cursor()
        sesion = request.json["idSesion"]
        cursor.execute("""SELECT tabDelegaciones.nomDelegacion, tabHistorial.turnos FROM tabDelegaciones
                    INNER JOIN tabHistorial ON tabDelegaciones.idDelegacion = tabHistorial.idDelegacion 
                    WHERE tabHistorial.idSesion = %s
                    ORDER BY tabHistorial.idHistorial""", (sesion,))
        historial = jsonify(cursor.fetchall())
        cursor.close()
        return historial

    @app.post("/POSTtiempos")
    def postTiempos():
        conn_POSTtiempos = pool.get_connection()
        try:
            cursor = conn.cursor()
            columna = request.json["columna"]
            segundos = request.json["segundos"]
            sesion = request.json["idSesion"]
            cursor.execute(f"UPDATE tabTiempos SET {columna} = %s WHERE idSesion = %s", (segundos, sesion))
            conn_POSTtiempos.commit()
            return {"ok": True}
        finally:
            conn_POSTtiempos.close()

    @app.get("/GETtiempos")
    def getTiempos():
        conn_GETtiempos = pool.get_connection()
        try:
            cursor = conn_GETtiempos.cursor()
            sesion = request.json["idSesion"]
            cursor.execute("SELECT leer, cuestionar, pensar, contestar FROM tabTiempos WHERE idSesion = %s", (sesion,))
            tiempos = cursor.fetchone()
            cursor.close()
            return jsonify(tiempos) 
        finally:
            conn_GETtiempos.close()

    @socketio.on("conteoDelegacion")
    def conteoDelegacion(data):
        print(data)
        nomDelegacion = data["nomDelegacion"]
        tiempo = data["tiempo"]
        sesion = data["idSesion"]
        socketio.emit("cuenta regresiva",{
                "delegacion": nomDelegacion,
                "tiempo": tiempo
                },room=str(sesion))

    @app.post("/POSTobservacion")
    def postObservacion():
        conexion_POSTobservacion = pool.get_connection()
        try:
            cursor = conexion_POSTobservacion.cursor()
            sesion = request.json["idSesion"]
            params = request.json["params"]
            sesion = request.json["idSesion"]
            cursor.execute("""INSERT INTO tabPuntaje (idDelegado, idSesion, idObs, descObs, puntaje)
                                SELECT idDelegado, %s, %s, %s, %s
                                FROM tabDelegados
                                WHERE tabDelegados.nomDelegado = %s""", (sesion, params[0], params[1], params[2], params[3]))
            conexion_POSTobservacion.commit()
            return {"ok": True}
        finally:
            conexion_POSTobservacion.close()

    @app.get("/GETobservaciones")
    def getObservaciones():
        conexion_GETobservaciones = pool.get_connection()
        try:
            cursor = conexion_GETobservaciones.cursor()
            sesion = request.json["idSesion"]
            cursor.execute("""SELECT tabDelegaciones.nomDelegacion, tabDelegados.nomDelegado, tabPuntaje.descObs, tabPuntaje.puntaje FROM tabPuntaje
                            INNER JOIN tabDelegados ON tabDelegados.idDelegado = tabPuntaje.idDelegado
                            INNER JOIN tabDelegaciones ON tabDelegaciones.idDelegacion = tabDelegados.idDelegacion WHERE tabPuntaje.idSesion = %s
                            ORDER BY nomDelegacion DESC""", (sesion,))
            observaciones = cursor.fetchall()
            if observaciones:
                return observaciones
            else:
                return {"ok": True}
        finally:
            conexion_GETobservaciones.close()

    @app.post("/POSTdelegados")
    def postDelegados():
        conexion_POSTdelegados = pool.get_connection()
        try:
            cursor = conexion_POSTdelegados.cursor()
            sesion = request.json["idSesion"]
            delegacion = request.json["delegacion"]
            cursor.execute("""UPDATE tabDelegaciones SET idSesion = %s WHERE nomDelegacion = %s""", (sesion, delegacion))
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
                                    WHERE tabDelegados.idDelegacion = tabDelegaciones.idDelegacion);""", (delegacion, delegacion, ))
            conexion_POSTdelegados.commit()
            return {"ok": True}
        finally:
            conexion_POSTdelegados.close()

    @app.get("/GETdelegados")
    def getDelegados():
        conexion_GETdelegados = pool.get_connection()
        try:
            cursor = conexion_GETdelegados.cursor()
            try:
                sesion = request.json("idSesion")
                cursor.execute("""SELECT * FROM tabDelegados 
                INNER JOIN tabDelegaciones 
                ON tabDelegados.idDelegacion = tabDelegaciones.idDelegacion
                WHERE idSesion = %s""", (sesion,))

            except:
                cursor.execute("""SELECT * FROM tabDelegados 
                                INNER JOIN tabDelegaciones 
                                ON tabDelegados.idDelegacion = tabDelegaciones.idDelegacion""")
            delegados = cursor.fetchall()
            return delegados
        finally:
            conexion_GETdelegados.close()

    @socketio.on("POSTnomDelegados")
    def postNomDelegados(data):
        conexion_POSTnomDelegados = pool.get_connection()
        try:
            cursor = conexion_POSTnomDelegados.cursor()
            nombre = data["nombre"]
            idDelegado = data["idDelegado"]
            cursor.execute("""UPDATE tabDelegados SET nomDelegado = %s WHERE idDelegado = %s""",(nombre, idDelegado)),
            conexion_POSTnomDelegados.commit()
        finally:
            conexion_POSTnomDelegados.close()

if __name__ == "__main__":
    socketio.run(app, debug=True)

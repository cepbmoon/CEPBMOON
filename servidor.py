from flask import *
import mysql.connector


conn = mysql.connector.connect(database="db_CEPBMOON",
                        user="avnadmin",
                        host="cepbmoon-cepb-moon.c.aivencloud.com",
                        password="AVNS_tHX9YWtgYm64fJwHvSo",
                        port=27526)
cursor = conn.cursor(dictionary=True)

# app = Flask(__name__)
# @app.get("/fila_delegaciones")
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
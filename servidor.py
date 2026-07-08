from flask import Flask

app = Flask(__name__)

@app.get("/obtener_botones")
def obtener_botones():

    cursor.execute("""
        SELECT texto
        FROM botones
        WHERE sesion_id = %s
    """, (...))

    return [...]
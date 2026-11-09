from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)

def validar_usuario(usuario):
    return re.fullmatch(r"[a-zA-Z0-9_]{4,20}", usuario) is not None

def validar_correo(correo):
    return re.fullmatch(
        r"^([a-za-Z0-9_\-\,]+)@([a-zA-Z0-9-_\-\.]+)\.([a-zA-Z]{2,5})$",
    ) is not None

def validar_password(password):
    return len(password) >= 8
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        #saneamiento y normalizacion de datos
        usuario = request.form.get("usuario","").strip()
        correo = request.form.get("correo","").strip()
        password = request.form.get("password","")

        #validaciones de formato
        if not validar_usuario(usuario):
            return"usuario valido"

        if not validar_correo(correo):
            return"correo eletronico invalido"

        if not validar_password(password):
            return"la contraseña debe contener al menos 8 caracteres"

        conexion = sqlite3.connect("usuarios.db")
        cursor = conexion.cursor()

        # verificar usuario duplicados
        cursor.execute(
        "SELECT id FROM usuario WHERE usuario = ?", 
        (usuario, correo)
         )
        existente = cursor.fetchone()
        if existente:
            conexion.close()
            return"El usuario o correo ya está registrado"

        #Generer has de a contraseña y guaradar en la base de datos
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO usuarios (usuario, correo, password) VALUES (?,?,?)",
            (usuario, correo, password_hash)
        )
        conexion.commit()
        conexion.close()

        return"Usuario registrado"

    return render_template("registro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method =="POST":
        usuario = request.form.get("usuario","").strip()
        password = request.form.get("password","")

        conexion = sqlite3.connect("usuarios.db")
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = ?", 
            (usuario,)
        )
        resultado = cursor.fetchone()
        conexion.close()

        if resultado and check_password_hash(resultado[3], password):
            return "Inicio de sesión correcto"
        else:
         return "credenciales incorrectas"

    return render_template("login.html")
if __name__ == "__main__":
    app.run(debug=True)


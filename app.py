import jwt
import os
from datetime import datetime, timedelta
from flask import request
from main import products
from functools import wraps
from flask import Flask, jsonify

app = Flask(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify(message="Token ausente ou malformado!"), 403
        token = auth_header.split()[1]
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify(message="Token expirado!"), 401
        except jwt.InvalidTokenError:
            return jsonify(message="Token inválido!"), 403
        return f(*args, **kwargs)
    return decorated

# Chave secreta para encriptação (ideal usar variável de ambiente em produção)
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-super-secreta")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify(message="Dados de login não fornecidos!"), 400
    if "username" not in data or "password" not in data:
        return jsonify(message="Campos 'username' e 'password' são obrigatórios!"), 400
    if data["username"] == "admin" and data["password"] == "123":
        # Gerar o token com expiração
        token = jwt.encode(
            {"user": data["username"], "exp": datetime.utcnow() + timedelta(minutes=30)},
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify(token=token)

    return jsonify(message="Credenciais inválidas!"), 401

@app.route("/protected", methods=["GET"])
def protected():
    # Obtém o token do cabeçalho da requisição
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify(message="Token é necessário!"), 403

    parts = auth_header.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return jsonify(message="Cabeçalho de autorização malformado!"), 401
    token = parts[1]

    try:
        # Decodifica o token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify(message=f"Bem-vindo, {decoded['user']}!")
    except jwt.ExpiredSignatureError:
        return jsonify(message="Token expirado! Faça login novamente."), 401
    except jwt.InvalidTokenError:
        return jsonify(message="Token inválido!"), 403

# Rota inicial (hello world)
@app.route("/")
def home():
    return jsonify(message="Bem-vindo à API segura com JWT!")

if __name__ == "__main__":
    app.run(debug=True)
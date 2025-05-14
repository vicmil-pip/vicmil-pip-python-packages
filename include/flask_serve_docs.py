import sys, pathlib, json
sys.path.append(str(pathlib.Path(__file__).resolve().parents[0]))

import vicmil_pip.packages.pyUtil as pyUtil

pip_manager = pyUtil.PipManager()
pip_manager.add_module("flask", "flask")
pip_manager.add_module("werkzeug", "werkzeug")
pip_manager.add_module("eventlet", "eventlet")
pip_manager.include_other_venv()
pip_manager.install_missing_modules()

import sys, pathlib, json
from flask import Flask, request, redirect, url_for, session, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash
import os

def create_app(secret_key, public_docs_dir, private_docs_dir, users_file):
    # Initialize the Flask app
    app = Flask(__name__)
    app.secret_key = secret_key  # Use the secret key passed as parameter

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,  # Only over HTTPS
        SESSION_COOKIE_SAMESITE='Lax'  # Or 'Strict' if possible
    )

    def load_users():
        try:
            with open(users_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_users(users):
        with open(users_file, "w") as f:
            json.dump(users, f, indent=4)

    def change_user_password(username, new_password):
        users = load_users()
        if username in users:
            users[username]["hashed_password"] = generate_password_hash(new_password)
            users[username]["version"] += 1
            save_users(users)

    users = load_users()

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user = request.form['username']
            pw = request.form['password']
            if user in users and check_password_hash(users[user]["hashed_password"], pw):
                session['user'] = user
                session['password_version'] = users[user]["version"]
                return redirect(url_for('docs'))
            return "Invalid credentials", 403

        return send_from_directory(public_docs_dir, "login.html")

    def is_session_valid():
        user = session.get('user')
        version = session.get('password_version')
        return (
            user in users and
            version == users[user]["version"]
        )

    @app.route('/logout', methods=['POST', 'GET'])
    def logout():
        session.pop('user', None)
        return redirect(url_for('login'))

    @app.route('/private_docs/<path:filename>')
    def serve_private_docs(filename):
        if 'user' not in session:
            return redirect(url_for('login'))

        if session['user'] not in users.keys():
            return redirect(url_for('login'))

        return send_from_directory(private_docs_dir, filename)

    @app.route('/public_docs/<path:filename>')
    def serve_public_docs(filename):
        return send_from_directory(public_docs_dir, filename)

    @app.route('/')
    def docs():
        if 'user' not in session:
            return redirect(url_for('serve_public_docs', filename='index.html'))
        return redirect(url_for('serve_private_docs', filename='index.html'))

    return app

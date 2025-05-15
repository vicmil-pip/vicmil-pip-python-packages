try:
    import eventlet
    eventlet.monkey_patch()  # Required for Flask-SocketIO with eventlet
except ImportError:
    pass

import sys, pathlib, json
sys.path.append(str(pathlib.Path(__file__).resolve().parents[0]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[5]))

from vicmil_pip.packages.pyUtil import *
from vicmil_pip.packages.pyFlaskBlueprints.include.user_manager import UserManager

pip_manager = PipManager()
pip_manager.add_module("flask", "flask")
pip_manager.add_module("werkzeug", "werkzeug")
pip_manager.add_module("eventlet", "eventlet")
pip_manager.add_module("flask_socketio", "flask-socketio")
pip_manager.include_other_venv()
pip_manager.install_missing_modules()

import sys, pathlib, json
from flask import Flask, request, redirect, url_for, session, send_from_directory, send_file, Blueprint, render_template, abort, flash
from werkzeug.exceptions import NotFound
from werkzeug.security import check_password_hash, generate_password_hash
from flask_socketio import SocketIO, emit
from jinja2 import FileSystemLoader, Environment, TemplateNotFound, select_autoescape
import os
import secrets
from typing import Dict, Optional


def create_app(secret_key_path: str = get_directory_path(__file__) + "/flask_secret.txt"):
    # Initialize the Flask app
    app = Flask(__name__)

    if not os.path.exists(secret_key_path):
        # Generate a new secret key if none were provided
        print("Creating new secret!")
        with open(secret_key_path, "w+") as file:
            file.write(secrets.token_urlsafe(32))

    with open(secret_key_path, "r") as file:
        # Read the secret key for the app
        app.secret_key = file.read()  # Use the secret key passed as parameter

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,  # Only over HTTPS
        SESSION_COOKIE_SAMESITE='Lax'  # Or 'Strict' if possible
    )

    socketio = SocketIO(app)

    return app, socketio


def serve_app(app: Flask, socketio: SocketIO, port=5000, host="127.0.0.1"):
    socketio.run(app, host=host, port=port)


def add_redirect_route(app: Flask, source_route: str, dst_route: str):
    def redirect_route():
        return redirect(dst_route)
    
    # Unique endpoint name for each route (avoid duplicates)
    endpoint_name = f"redirect_route_{source_route.replace('/', '_')}"
    app.add_url_rule(f'{source_route}', endpoint=endpoint_name, view_func=redirect_route)


class UserFlaskApp:
    def __init__(self, app: Flask, user_manger: UserManager):
        self.app = app
        self.user_manager: UserManager = user_manger
        self.session_user_token = "user"
        self.password_version_token = "password_version"
        self.not_logged_in_route = "/login"
        self.insufficient_permissions_route = "/"


    def redirect_on_404(self, destination_route: str):
        """Redirects to a given route when a 404 occurs."""
        @self.app.errorhandler(404)
        def handle_404(e):
            flash("Page not found. You were redirected.")
            return redirect(destination_route)


    def serve_template_folder(
        self,
        template_name: str,
        folder_path: str, 
        required_permissions: Optional[list] = None):

        blueprint_name = f"bp_{template_name.replace('/', '_')}"

        # Create blueprint with the template folder
        blueprint = Blueprint(
            name=blueprint_name,
            import_name=__name__,
            url_prefix=f"/{template_name}"
        )

        # Create a separate Jinja2 environment for this blueprint
        jinja_env = Environment(
            loader=FileSystemLoader(folder_path),
            autoescape=select_autoescape(['html', 'xml'])
        )

        def handle_template(filename):
            try:
                if self.session_user_token in session:
                    username = session[self.session_user_token]
                    user_role = self.user_manager.get_role(username)
                    print("user logged in")
                else:
                    username = None
                    user_role = None
                    print("user not logged in")

                if required_permissions:
                    if self.session_user_token not in session:
                        print("user not logged in")
                        return redirect(self.not_logged_in_route)

                    username = session[self.session_user_token]
                    password_version = session[self.password_version_token]

                    if not self.user_manager.has_access(username, password_version, required_permissions):
                        print("user does not have access")
                        return redirect(self.insufficient_permissions_route)

                print("rendering template from:", folder_path, "file:", filename)

                # Use the custom Jinja environment to load and render the template
                template = jinja_env.get_template(filename)
                return template.render(username=username, user_role=user_role)

            except FileNotFoundError:
                return abort(404, description=f"File not found: {filename}")
            except TemplateNotFound:
                return abort(404, description=f"Template not found: {filename}")
            except NotFound:
                return abort(404, description=f"Route not found: {filename}")

        endpoint_name = f"serve_template_{template_name.replace('/', '_')}"
        blueprint.add_url_rule('/<path:filename>', endpoint=endpoint_name, view_func=handle_template)

        self.app.register_blueprint(blueprint)


    def serve_folder_route(
        self,
        route: str, 
        folder_path: str, 
        required_permissions: Optional[list] = None):

        def serve_folder(filename):
            try:
                if required_permissions:
                    if self.session_user_token not in session:
                        return redirect(self.not_logged_in_route)

                    username = session[self.session_user_token]
                    password_version = session[self.password_version_token]

                    if not self.user_manager.has_access(username, password_version, required_permissions):
                        return redirect(self.insufficient_permissions_route)

                return send_from_directory(folder_path, filename)

            except NotFound:
                return abort(404, description=f"File not found: {filename}")

        endpoint_name = f"serve_folder_{route.replace('/', '_')}"
        self.app.add_url_rule(f'{route}/<path:filename>', endpoint=endpoint_name, view_func=serve_folder)

    def add_login_route(self, redirect_route: str, html_file_path, route="/login"):
        redirect_route = redirect_route
        html_file_path = html_file_path

        def login():
            if request.method == 'POST':
                username = request.form['username']
                pw = request.form['password']

                if self.user_manager.verify_password(username, pw):
                    session[self.session_user_token] = username
                    session[self.password_version_token] = self.user_manager.get_password_version(username)
                    return redirect(redirect_route)
                return "Invalid credentials", 403

            return send_file(html_file_path)
        
        endpoint_name = f"login_{route.replace('/', '_')}"
        self.app.add_url_rule(
            f'{route}',
            endpoint=endpoint_name,
            view_func=login,
            methods=["GET", "POST"]
        )

    def add_function_route(self, route: str, func, methods=["GET", "POST"], required_permissions: Optional[list] = None):
        if not required_permissions:
            endpoint_name = f"route_{route.replace('/', '_')}"
            self.app.add_url_rule(
                f'{route}',
                endpoint=endpoint_name,
                view_func=func,
                methods=methods
            )
        else:
            def func_route():
                if required_permissions:
                    if self.session_user_token not in session:
                        return redirect(self.not_logged_in_route)

                    username = session[self.session_user_token]
                    password_version = session[self.password_version_token]

                    if not self.user_manager.has_access(username, password_version, required_permissions):
                        return redirect(self.insufficient_permissions_route)

                return func()
            
            endpoint_name = f"route_{route.replace('/', '_')}"
            self.app.add_url_rule(
                f'{route}',
                endpoint=endpoint_name,
                view_func=func_route,
                methods=methods
            )
        

    def add_logout_route(self, redirect_route: str, route="/logout"):
        redirect_route = redirect_route

        def logout():
            session.pop(self.session_user_token, None)
            return redirect(redirect_route)
        
        endpoint_name = f"logout_{route.replace('/', '_')}"
        self.app.add_url_rule(f'{route}', endpoint=endpoint_name, view_func=logout, methods=["GET", "POST"])





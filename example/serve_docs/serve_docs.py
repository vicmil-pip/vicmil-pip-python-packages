import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[0]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[5]))

from vicmil_pip.packages.pyFlaskBlueprints.include.flask_app_util import *

from flask import jsonify

secret_key_path = get_directory_path(__file__) + "/flask_secret.txt"
users_file = get_directory_path(__file__) + "/users.json"

app, socketio = create_app(secret_key_path)

add_redirect_route(app, "/", "/public/index.html")

user_manager_ = UserManager(users_file)

flask_app = UserFlaskApp(app=app, user_manger=user_manager_)

flask_app.serve_template_folder(
    template_name="public",
    folder_path=get_directory_path(__file__) + "/public_template",
    required_permissions=None
)


flask_app.serve_template_folder(
    template_name="user",
    folder_path=get_directory_path(__file__) + "/user_template",
    required_permissions=["user"]
)

flask_app.serve_folder_route(
    route="/admin",
    folder_path=get_directory_path(__file__) + "/admin",
    required_permissions=None
)

flask_app.add_login_route(
    route="/login",
    html_file_path=get_directory_path(__file__) + "/public/login.html",
    redirect_route="/user/documentation.html"
)

flask_app.add_logout_route(
    route="/logout",
    redirect_route="/"
)

def create_user_route():
    print("Create user")
    username = request.form['username']
    pw = request.form['password']
    flask_app.user_manager.add_user(username=username, password=pw)
    flask_app.user_manager.save_users()
    return redirect("/admin/index.html")


def delete_user_route():
    print("Delete user")
    username = request.form['username']
    if flask_app.user_manager.get_role(username=username) != "admin":
        flask_app.user_manager.remove_user(username)
        flask_app.user_manager.save_users()
        return redirect("/admin/index.html")
    
    return redirect("/admin/index.html")


def get_users():
    users = flask_app.user_manager.list_users()  # however you fetch users
    return jsonify([{"username": user} for user in users])
    

flask_app.add_function_route(route="/api/create_user", func=create_user_route, required_permissions=["admin"], methods=["POST"])
flask_app.add_function_route(route="/api/delete_user", func=delete_user_route, required_permissions=["admin"], methods=["POST"])
flask_app.add_function_route(route="/api/users", func=get_users, required_permissions=["admin"], methods=["POST", "GET"])


import os
if not os.path.exists(users_file):
    user_manager_.add_user(
        username="user1",
        password="123",
        permissions=[],
        role="admin"
    )

    user_manager_.add_user(
        username="user2",
        password="123",
        permissions=[]
    )

    user_manager_.save_users()
    

open_webbrowser("http://localhost:5000")
serve_app(app, socketio)
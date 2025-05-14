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

from vicmil_pip.packages.pyHostDocs import *

# Create another app with different parameters
users_file = pyUtil.get_directory_path(__file__) + "/users.json"
private_docs_dir = pyUtil.get_directory_path(__file__) + '/private_docs'
public_docs_dir = pyUtil.get_directory_path(__file__) + '/public_docs' 
secret_key = "eRyVT6209eETcR2"

app = create_app(
    secret_key=secret_key,  # App-specific secret key
    public_docs_dir=public_docs_dir,
    private_docs_dir=private_docs_dir,
    users_file=users_file
)

pip_manager = pyUtil.PipManager()
pip_manager.add_module("flask_socketio", "flask-socketio")
pip_manager.install_missing_modules()

from flask_socketio import SocketIO, emit
socketio = SocketIO(app)

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000)

# Login:
# username: user1
# password: 123
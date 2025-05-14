import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[0]))
sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[3]))

from packages.pyHostDocs.include.flask_serve_docs import *
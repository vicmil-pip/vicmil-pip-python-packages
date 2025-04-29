import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[0]))
sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[3]))
sys.path.append(str(Path(__file__).resolve().parents[4]))
sys.path.append(str(Path(__file__).resolve().parents[5]))

from vicmil_pip.packages.pyMkDocs import *

src_dir = get_directory_path(__file__)
docs_dir = get_directory_path(__file__) + "/docs"

vmdoc_generate(docs_dir=docs_dir, src_dir=src_dir)

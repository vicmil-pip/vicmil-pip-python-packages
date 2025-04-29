import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[0]))
sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[3]))
sys.path.append(str(Path(__file__).resolve().parents[4]))
sys.path.append(str(Path(__file__).resolve().parents[5]))

from vicmil_pip.packages.pyMkDocs import *

# The path where the documentation will be stored
docs_dir = get_directory_path(__file__) + "/docs"

# The path where to look for files with documentation
src_dir = get_directory_path(__file__, 2)

vmdoc_generate(docs_dir, src_dir)

"""
[vmdoc:description]
The init file with instructions for how to use the library
[vmdoc:enddescription]
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[0])) 

from include.mkdocs_build import *
from include.vmdoc import vmdoc_generate_markdown_files



"""
[vmdoc:start]
## vicmil_generate_project_documentation

Specify directory to look for source files, and where you want docs directory
Then it automatically generates the documentation for you

```
def vicmil_generate_project_documentation(docs_dir: str, src_dir: str) -> None
```

Example
```
from vicmil_pip.packages.pyMkDocs import *

# The path where the documentation will be stored
docs_dir = get_directory_path(__file__) + "/docs"

# The path where to look for files with documentation
src_dir = get_directory_path(__file__, 2)

vicmil_generate_project_documentation(docs_dir, src_dir)
```

[OPTIONAL]: You can also specify what files you want to include/exclude using syntax like .gitignore

```
from vicmil_pip.packages.pyMkDocs import *

# The path where the documentation will be stored
docs_dir = get_directory_path(__file__) + "/docs"

# The path where to look for files with documentation
src_dir = get_directory_path(__file__, 2)

# The files to include
gitignore_content = \"""
        # Exclude everything by default
        *

        # Include code files
        !*.py
        !*.cpp
        !*.h
        !*.hpp
        !*.java
        !*.js

        # Exclude directories
        venv/*
        node_modules/*
        build/*
        dist/*

        # Exclude specific log files
        *.log
        *.tmp
        \"""

vicmil_generate_project_documentation(docs_dir, src_dir, gitignore_content)
```
[vmdoc:end]
"""
def vicmil_generate_project_documentation(docs_dir: str, src_dir: str) -> None:
    # Ensure the mkdocs project is setup in the docs folder
    ensure_mkdocs_project_setup(docs_dir)

    # Build mkdocs files based on vmdoc documentation
    output_dir = docs_dir + "/docs/vmdoc"
    os.makedirs(output_dir, exist_ok=True)
    vmdoc_generate_markdown_files(src_dir, output_dir)

    # Compile project and show the result in the browser
    compile_mkdocs(docs_dir)


def generate_package_documentation(package_name: str):
    # The path where the documentation will be stored
    docs_dir = get_directory_path(__file__, 1) + "/packageDocs"

    if os.path.exists(docs_dir):
        docs_dir = docs_dir + "/" + package_name
        # The path where to look for files with documentation
        src_dir = get_directory_path(__file__)

        vicmil_generate_project_documentation(docs_dir, src_dir)

    else:
        print(f"path {docs_dir} does not exist!")
---
title: __init__.py
source_file: __init__.py
description: The init file with instructions for how to use the library
generated_from: vmdoc
source_code_file: init.py_743b1a.txt
---

[📄 View raw source code](init.py_743b1a.txt)

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


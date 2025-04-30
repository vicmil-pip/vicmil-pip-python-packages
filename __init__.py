"""
[vmdoc:description]
The init file with instructions for how to use the library
[vmdoc:enddescription]
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[0])) 

from include.mkdocs_build import *
from include.vmdoc import VmDocsGenerator, update_nav_section
import shutil



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
def vmdoc_generate(docs_dir: str, src_dir: str, show_in_browser: bool = True, gitignore_content: str = None) -> None:
    # Ensure the mkdocs project is setup in the docs folder
    if not os.path.exists(docs_dir):
        mkdocs_default_project(docs_dir)

    # Build mkdocs files based on vmdoc documentation
    vmdoc_generator = VmDocsGenerator(docs_dir)
    
    if gitignore_content:
        vmdoc_generator.set_pattern(gitignore_content)

    vmdoc_generator.add_files_in_dir(src_dir)
    vmdoc_generator.generate()

    # Compile project and show the result in the browser
    compile_mkdocs(docs_dir, show_in_browser=show_in_browser)


"""
Combine multiple mkDocs repos into a single one
- Allows searching in all repos at once
- Keep all documentation in one place
"""
class VmDocsMonoRepoGenerator:
    def __init__(self, docs_dir: str):
        self._added_projects = []
        self.docs_dir = docs_dir

    def add_project(self, doc_path: str, project_name: str):
        if not is_mkdocs_project(doc_path):
            return
        
        self._added_projects.append((doc_path, project_name))
    

    def update_nav(self):
        # Update nav/projects with new data
        project_entries = list()

        projects_dir = f"{self.docs_dir}/projects"
        if not os.path.exists(projects_dir):
            print(f"Invalid path: {projects_dir}")
            return

        projects = list_mkdocs_projects(projects_dir)
        for project_name in projects:
            project_entries.append((project_name, f"!include ./projects/{project_name}/mkdocs.yml"))

        print(project_entries)

        update_nav_section(f"{self.docs_dir}/mkdocs.yml", "projects", project_entries)
    

    def generate(self, show_in_browser: bool = True):
        if not os.path.exists(self.docs_dir):
            mkdocs_monorepo_project(self.docs_dir)

        # Copy all the repos to the target
        for path, project_name in self._added_projects:
            output_path = self.docs_dir + "/projects/" + project_name
            print(f"copy {path} to {output_path}")
            safe_copy_directory_with_ignore(path, output_path, "site/*")

        self.update_nav()
        compile_mkdocs(self.docs_dir, show_in_browser=show_in_browser)

        

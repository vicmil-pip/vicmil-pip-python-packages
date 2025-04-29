import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[0]))
sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[3]))
sys.path.append(str(Path(__file__).resolve().parents[4]))
sys.path.append(str(Path(__file__).resolve().parents[5]))

from vicmil_pip.packages.pyMkDocs import *

base_docs = get_directory_path(__file__) + "/docs"

project1 = base_docs + "/docs1"
project2 = base_docs + "/docs2"

if not os.path.exists(project1):
    mkdocs_default_project(project1, site_name="Project1")
    

if not os.path.exists(project2):
    mkdocs_default_project(project2, site_name="Project2")

compile_mkdocs(project1, show_in_browser=False)
compile_mkdocs(project2, show_in_browser=False)

mono_repo = base_docs + "/docs_mono"
mono_repo_generator = VmDocsMonoRepoGenerator(mono_repo)
mono_repo_generator.add_project(project1, "project1")
mono_repo_generator.add_project(project2, "project2")

mono_repo_generator.generate()






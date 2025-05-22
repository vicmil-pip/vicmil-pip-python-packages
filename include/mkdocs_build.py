import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[0]))
sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[3]))
sys.path.append(str(Path(__file__).resolve().parents[4]))
sys.path.append(str(Path(__file__).resolve().parents[5]))

from vicmil_pip.packages.pyUtil import *

pip_manager = PipManager()
pip_manager.add_pip_package("mkdocs")
pip_manager.add_pip_package("mkdocs-material")
pip_manager.add_pip_package("pymdown-extensions")


def is_mkdocs_project(path):
    return os.path.isfile(os.path.join(path, 'mkdocs.yml')) and os.path.isdir(os.path.join(path, 'docs'))


def list_mkdocs_projects(dir_path: str):
    """
    Returns a list of mkdocs projects in repo, relative to the dir path
    """
    mkdocs_projects = list()
    for project in sorted(os.listdir(dir_path)):
        proj_path = os.path.join(dir_path, project)
        if is_mkdocs_project(proj_path):
            mkdocs_projects.append(project)

    return mkdocs_projects


def mkdocs_default_project(docs_path: str, site_name: str = "My Docs " + generate_random_numbers(6)):
    pip_manager.install_missing_modules()

    import mkdocs
    import mkdocs.utils
    # Create the project directory and docs directory
    os.makedirs(docs_path+"/docs", exist_ok=True)

    # Write default mkdocs.yml file
    config_content = \
f"""site_name: {site_name}

theme:
  name: material

  features:
    - content.code.copy

  palette:
  # Palette toggle for light mode
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle:
        icon: material/toggle-switch-off-outline
        name: Switch to dark mode

    # Palette toggle for dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle:
        icon: material/toggle-switch
        name: Switch to light mode

nav:
  - Home: index.md
  - vmdoc: vmdoc/vmdocs.md
markdown_extensions:
  - codehilite:
      guess_lang: false  # Ensures correct language highlighting
  - fenced_code
  - pymdownx.superfences
  - pymdownx.tabbed
  - attr_list
"""
    mkdocs.utils.write_file(config_content.encode('utf-8'), docs_path + "/mkdocs.yml")

    # Write default index.md file
    index_content = f"# Welcome to {site_name}\n\nThis is your homepage!"
    mkdocs.utils.write_file(index_content.encode('utf-8'), docs_path + "/docs/index.md")

    print(f"New MkDocs project created in: {docs_path}")


# Combine multiple mkdocs projects into one
def mkdocs_monorepo_project(docs_path: str):
    pip_manager.add_pip_package("mkdocs-monorepo-plugin")
    pip_manager.install_missing_modules()

    import mkdocs
    import mkdocs.utils
    # Create the project directory and docs directory
    os.makedirs(docs_path+"/docs", exist_ok=True)

    # Write default mkdocs.yml file
    config_content = \
"""site_name: Combined MkDocs Site

theme:
  name: material

  features:
    - content.code.copy

  palette:
  # Palette toggle for light mode
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle:
        icon: material/toggle-switch-off-outline
        name: Switch to dark mode

    # Palette toggle for dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle:
        icon: material/toggle-switch
        name: Switch to light mode

nav:
  - Home: index.md

markdown_extensions:
  - codehilite:
      guess_lang: false  # Ensures correct language highlighting
  - fenced_code
  - pymdownx.superfences
  - pymdownx.tabbed
  - attr_list
plugins:
  - monorepo
  - search
"""
    mkdocs.utils.write_file(config_content.encode('utf-8'), docs_path + "/mkdocs.yml")

    # Write default index.md file
    index_content = "# Welcome to MkDocs\n\nThis is your homepage!"
    mkdocs.utils.write_file(index_content.encode('utf-8'), docs_path + "/docs/index.md")

    mkdocs.utils.write_file(index_content.encode('utf-8'), docs_path + "/projects/project1/docs/index.md")
    mkdocs.utils.write_file(index_content.encode('utf-8'), docs_path + "/projects/project2/docs/index.md")

    mkdocs.utils.write_file("""
site_name: Project1
nav:
  - Home: index.md    
""".encode('utf-8'), docs_path + "/projects/project1/mkdocs.yml")
    
    mkdocs.utils.write_file("""
site_name: Project2
nav:
  - Home: index.md    
""".encode('utf-8'), docs_path + "/projects/project2/mkdocs.yml")

    print(f"New MkDocs project created in: {docs_path}")


def serve_mkdocs_project(docs_path, host="127.0.0.1", port=8000):
    """
    Serve an MkDocs project locally.

    Args:
        config_file (str): Path to the mkdocs.yml configuration file.
        host (str): Host address to bind the server (default: 127.0.0.1).
        port (int): Port number to serve the site (default: 8000).
    """
    pip_manager.install_missing_modules()
    config_file = docs_path + "/mkdocs.yml"
    import mkdocs
    import mkdocs.commands.serve
    try:
        # Start the MkDocs development server directly with the configuration file
        print(f"Serving MkDocs at http://{host}:{port}")
        mkdocs.commands.serve.serve(config_file, host=host, port=port, livereload=True, watch_theme=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")


def build_mkdocs_documentation(docs_path):
    pip_manager.install_missing_modules()
    import mkdocs
    from mkdocs.config import load_config
    from mkdocs.commands.build import build
    """
    Build MkDocs documentation into a static site.

    Args:
        config_file (str): Path to the mkdocs.yml configuration file.
        output_dir (str): Optional. Path to the output directory for the built site.
    """
    config_file = docs_path + "/mkdocs.yml"
    output_dir = docs_path + "/site"
    # Load the MkDocs configuration
    config = load_config(config_file)
    
    # Set a custom output directory if provided
    if output_dir:
        config['site_dir'] = os.path.abspath(output_dir)
    
    try:
        print(f"Building documentation using config: {config_file}")
        build(config)
        print(f"Documentation successfully built in: {config['site_dir']}")
    except Exception as e:
        print(f"Error while building documentation: {e}")


def compile_mkdocs(docs_path: str, show_in_browser: bool = True):
    if not os.path.exists(docs_path):
        mkdocs_default_project(docs_path)
    build_mkdocs_documentation(docs_path)

    if show_in_browser:
        open_webbrowser("http://127.0.0.1:8000")
        serve_mkdocs_project(docs_path)
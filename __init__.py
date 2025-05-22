import pathlib
import os
import platform
import importlib
import sys
import shutil
import fnmatch
import hashlib
import string
import random
from typing import List, Dict
sys.path.append(str(pathlib.Path(__file__).resolve().parents[0]))


def get_directory_path(__file__in, up_directories=0):
    return str(pathlib.Path(__file__in).parents[up_directories].resolve()).replace("\\", "/")


def run_command(command: str) -> None:
    """Run a command in the terminal"""
    if platform.system() == "Windows": # Windows
        win_command = None
        if command[0] != '"':
            win_command = f'powershell; {command}'
        else:
            win_command = f'powershell; &{command}'

        print("running command: ", f'{win_command}')
        os.system(win_command)
    else:
        print("running command: ", f'{command}')
        os.system(command)


def python_virtual_environment(env_directory_path):
    # Setup a python virtual environmet
    os.makedirs(env_directory_path, exist_ok=True) # Ensure directory exists
    run_command(f'"{sys.executable}" -m venv "{env_directory_path}"')


def get_venv_site_packages_path(venv_path):
    """Returns the site-packages path for a given virtual environment."""
    python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    
    # Construct the expected site-packages path
    if platform.system() == "Windows": # Windows
        site_packages_path = os.path.join(venv_path, "Lib", "site-packages")
    else:  # macOS/Linux
        site_packages_path = os.path.join(venv_path, "lib", python_version, "site-packages")

    return site_packages_path if os.path.exists(site_packages_path) else None


def get_venv_pip_path(env_directory_path):
    if platform.system() == "Windows":
        # The path may vary on windows, so we need to check for both the scripts path and the bin path
        script_path = f'{env_directory_path}/Scripts/pip'
        if os.path.exists(script_path):
            return script_path
        bin_path = f'{env_directory_path}/bin/pip'
        return bin_path
    else:
        return f'{env_directory_path}/bin/pip'


def pip_install_packages_in_virtual_environment(env_directory_path, packages):
    if not os.path.exists(env_directory_path):
        print("Invalid path")
        raise Exception("Invalid path")
    
    for package in packages:
        run_command(f'"{get_venv_pip_path(env_directory_path)}" install {package}')


def module_installed(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False
    

def include_other_venv(other_venv_path: str):
    site_package_path = get_venv_site_packages_path(other_venv_path)
    if not other_venv_path in sys.path:
        print("Updating sys.path with other venv", site_package_path)
        sys.path.append(site_package_path)  # Add other venv's site-packages to sys.path


def parse_requirements(file_path):
    requirements = []
    with open(file_path, 'r') as f:
        for line in f:
            # Strip whitespace and ignore comments or empty lines
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Remove inline comments
            line = line.split('#')[0].strip()

            requirements.append(line)

    return requirements


def open_webbrowser(url: str):
    import webbrowser
    webbrowser.open(url, new=0, autoraise=True)


def serve_html_page(html_file_path: str):
    import webbrowser
    """ Start the webbrowser if not already open and launch the html page

    Parameters
    ----------
        html_file_path (str): The path to the html file that should be shown in the browser

    Returns
    -------
        None
    """
    os.chdir(get_directory_path(html_file_path, 0))
    if not (os.path.exists(html_file_path)):
        print("html file does not exist!")
        return
    
    file_name: str = html_file_path.replace("\\", "/").rsplit("/", maxsplit=1)[-1]
    webbrowser.open("http://localhost:8000/" + file_name, new=0, autoraise=True)

    try:
        run_command(f'"{sys.executable}" -m http.server --bind localhost')
    except Exception as e:
        pass


class PipManager:
    def __init__(self):
        self._modules = list()
        self.venv_path = get_directory_path(__file__) + "/venv"
        self.installed_pip_packages = list()

    def add_module(self, module_name: str, pip_package_if_missing: str):
        self._modules.append((module_name, pip_package_if_missing))

    def add_pip_package(self, pip_package: str):
        self._modules.append((None, pip_package))

    def add_requirements_file(self, requirements_file_path):
        requirements = parse_requirements(requirements_file_path)
        for requirement in requirements:
            self.add_pip_package(requirement)

    def include_other_venv(self):
        include_other_venv(self.venv_path)

    def install_missing_modules(self):
        """
        [vmdoc:start]
        # PipManager.install_missing_modules()

        Tries to see if the module is available, 
            if it fails, it installs the missing pip packages inside self.venv_path
        [vmdoc:end]
        """
        missing_pip_packages = set()

        for module_name, pip_package in self._modules:
            if not module_name or not module_installed(module_name=module_name):
                if not pip_package in self.installed_pip_packages:
                    missing_pip_packages.add(pip_package)
                    self.installed_pip_packages.append(pip_package)

        if len(missing_pip_packages) > 0:
            if not os.path.exists(self.venv_path):
                python_virtual_environment(self.venv_path)

            missing_pip_packages = list(missing_pip_packages)
            pip_install_packages_in_virtual_environment(self.venv_path, missing_pip_packages)

            self.include_other_venv()


def safe_copy_directory(src, dst):
    """
    Recursively copies contents of src to dst safely, avoiding recursion issues.
    
    Parameters:
    src (str): Source directory path.
    dst (str): Destination directory path.
    """
    src = pathlib.Path(src).resolve()
    dst = pathlib.Path(dst).resolve()

    # Prevent recursive copy into subdirectory of itself
    if dst in src.parents or src == dst:
        raise ValueError("Destination cannot be the source or inside the source.")

    if not src.is_dir():
        raise NotADirectoryError(f"Source directory '{src}' does not exist or is not a directory.")

    os.makedirs(dst, exist_ok=True)

    for root, dirs, files in os.walk(src):
        rel_path = pathlib.Path(root).relative_to(src)
        target_dir = dst / rel_path
        os.makedirs(target_dir, exist_ok=True)

        for file in files:
            src_file = pathlib.Path(root) / file
            dst_file = target_dir / file
            shutil.copy2(src_file, dst_file)


def delete_folder_with_contents(file: str):
    if os.path.exists(file):
        shutil.rmtree(file)  # Deletes the folder and its contents


def safe_copy_directory_with_ignore(src, dst, gitignore_str):
    """
    Recursively copies contents of src to dst safely, ignoring files/directories 
    that match gitignore-style patterns using a custom pattern matcher.

    Parameters:
    src (str): Source directory path.
    dst (str): Destination directory path.
    gitignore_str (str): Gitignore-style pattern string.
    """
    src = pathlib.Path(src).resolve()
    dst = pathlib.Path(dst).resolve()

    if dst in src.parents or src == dst:
        raise ValueError("Destination cannot be the source or inside the source.")

    if not src.is_dir():
        raise NotADirectoryError(f"Source directory '{src}' does not exist or is not a directory.")
    
    delete_folder_with_contents(dst)

    # Initialize and load patterns
    pattern_matcher = GitignorePatternMatcher()
    pattern_matcher.add_pattern_str(gitignore_str)

    os.makedirs(dst, exist_ok=True)

    for root, dirs, files in os.walk(src):
        rel_path = pathlib.Path(root).relative_to(src)

        # Prune ignored directories in-place to avoid descending into them
        dirs[:] = [d for d in dirs if pattern_matcher.include_file(rel_path / d)]

        target_dir = dst / rel_path
        os.makedirs(target_dir, exist_ok=True)

        for file in files:
            relative_file_path = rel_path / file
            if pattern_matcher.include_file(relative_file_path):
                src_file = pathlib.Path(root) / file
                dst_file = target_dir / file
                shutil.copy2(src_file, dst_file)


def write_text_to_file(file_path: str, contents: str):
    """
    Writes the given contents to a file at the specified file path.

    Args:
        file_path (str): The path to the file where the text will be written.
        contents (str): The text content to write to the file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(contents)


def list_installed_vicmil_packages():
    dirs = os.listdir(get_directory_path(__file__, 1))        
    vicmil_packages = list()
    for f in dirs:
        if f == "__pycache__":
            continue
        if f == "venv":
            continue
        vicmil_packages.append(f)

    return vicmil_packages
    

class GitignorePatternMatcher:
    """
    Pattern match just like .gitignore files
    """
    def __init__(self):
        self.pattern_list = list()

    def add_pattern_str(self, gitignore_content: str):
        for line in gitignore_content.splitlines():
            if len(line) == 0:
                continue

            line = line.split('#')[0].strip()
            if not line:
                continue

            line_starts_with_excl = line.startswith('!')
            pattern = line[1:] if line_starts_with_excl else line
            self.pattern_list.append((pattern, line_starts_with_excl))


    def include_file(self, file_path: str):
        include_file = True  # Default: include file

        for pattern, line_starts_with_excl in self.pattern_list:
            if fnmatch.fnmatch(file_path, pattern):
                include_file = line_starts_with_excl  # Override based on whether it's a negation (!)
        
        return include_file
    

    def ignore_file(self, file_path: str):
        return not self.include_file(file_path)


    def list_matching_files(self, directory_path: str):
        """Return files matching the gitignore-like pattern list."""
        matching_files = []

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), directory_path).replace("\\", "/")
                if self.include_file(rel_path):
                    matching_files.append(os.path.join(root, file))

        return matching_files

    
import subprocess
def invoke_python_file_using_subprocess(python_env_path: str, file_path: str, logfile_path: str = None) -> subprocess.Popen:
    if not os.path.exists(python_env_path):
        print(f"invalid path: {python_env_path}")

    if not os.path.exists(file_path):
        print(f"invalid path: {file_path}")

    current_directory = str(pathlib.Path(file_path).parents[0].resolve()).replace("\\", "/")
    os.chdir(current_directory) # Set active directory to the current directory

    command = ""
    my_os = platform.system()
    if logfile_path:
        if my_os == "Windows":
            command = f'powershell; &"{python_env_path}/Scripts/python" -u "{file_path}" > "{logfile_path}"'
        else:
            command = f'"{python_env_path}/bin/python" -u "{file_path}" > "{logfile_path}"'
    else:
        if my_os == "Windows":
            command = f'powershell; &"{python_env_path}/Scripts/python" -u "{file_path}"'
        else:
            command = f'"{python_env_path}/bin/python" -u "{file_path}"'

    new_process = subprocess.Popen(command, shell=True)
    return new_process


def find_files_by_name(root_dir, filename):
    matching_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file == filename:
                full_path = os.path.abspath(os.path.join(dirpath, file))
                matching_files.append(full_path)

    return matching_files


def delete_file(file: str):
    if os.path.exists(file):
        os.remove(file)


import tarfile
import zipfile

def untar_file(tar_path, extract_to, delete_tar=False):
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=extract_to)

    if delete_tar:
        delete_file(tar_path)


def unzip_file(zip_file_path: str, destination_folder: str, delete_zip=False):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)

    if delete_zip:
        delete_file(zip_file_path)


def unzip_without_top_dir(zip_file_path, destination_folder, delete_zip=False):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Get the list of file paths in the zip
        members = zip_ref.namelist()
        
        # Identify the top-level directory (assume first path element)
        top_level_dir = os.path.commonprefix(members).rstrip('/')
        
        for member in members:
            # Remove the top-level directory from the file path
            relative_path = os.path.relpath(member, top_level_dir)
            
            # Compute the final extraction path
            final_path = os.path.join(destination_folder, relative_path)

            if member.endswith('/'):  # Handle directories
                os.makedirs(final_path, exist_ok=True)
            else:  # Extract files
                os.makedirs(os.path.dirname(final_path), exist_ok=True)
                with zip_ref.open(member) as src, open(final_path, 'wb') as dst:
                    dst.write(src.read())

    if delete_zip:
        delete_file(zip_file_path)


def download_file_from_google_drive(drive_url: str, output_file: str):
    def _extract_id_from_url(url: str):
        url2 = url.split("drive.google.com/file/d/")[1]
        file_id = url2.split("/")[0]
        return file_id
    
    def _download_large_file_from_google_drive(id, destination):
        pip_manager = PipManager()
        if not module_installed("gdown"):
            pip_manager.add_pip_package("gdown")
            pip_manager.install_missing_modules()

        import gdown

        # Construct the direct URL
        url = f"https://drive.google.com/uc?id={id}"

        # Download the file
        gdown.download(url, destination, quiet=False)

    file_id = _extract_id_from_url(drive_url)
    _download_large_file_from_google_drive(file_id, output_file)


def download_github_repo_as_zip(zip_url: str, output_zip_file: str):
    """Downloads a GitHub repository as a ZIP file.
    
    Args:
        repo_url (str): The URL of the GitHub repository (e.g., "https://github.com/owner/repo").
        output_file (str): The name of the output ZIP file (e.g., "repo.zip").
    """
    try:
        import requests
        response = requests.get(zip_url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses
        
        with open(output_zip_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        
        print(f"Download complete: {output_zip_file}")
    except Exception as e:
        print(f"Error: {e}")


def hash_path(rel_path: str) -> str:
    """Generate a short hash of the relative path."""
    return hashlib.md5(rel_path.encode('utf-8')).hexdigest()[:6]


def generate_random_letters(count=5):
    return ''.join(random.choices(string.ascii_lowercase, k=count))


def generate_random_numbers(count=5):
    return ''.join(str(random.randint(0, 9)) for _ in range(count))
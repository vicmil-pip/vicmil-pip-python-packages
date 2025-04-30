import pathlib
import os
import platform
import importlib
import sys
import shutil
import fnmatch
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
        return f'{env_directory_path}/Scripts/pip'
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

            include_other_venv(self.venv_path)
    

def copy_directory(src_dir, dest_dir):
    """
    Copies the contents of src_dir to dest_dir.
    If dest_dir exists, it remove its content
    """
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"Source directory '{src_dir}' does not exist.")
    
    # Remove dest_dir if it already exists
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    
    shutil.copytree(src_dir, dest_dir)


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

            is_negation = line.startswith('!')
            pattern = line[1:] if is_negation else line
            self.pattern_list.append((pattern, is_negation))


    def match_file(self, file_path: str):
        match = False  # Default: do not include

        for pattern, is_negation in self.pattern_list:
            if fnmatch.fnmatch(file_path, pattern):
                match = is_negation  # Override based on whether it's a negation (!)
        
        return match


    def list_matching_files(self, directory_path: str):
        """Return files matching the gitignore-like pattern list."""
        matching_files = []

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), directory_path).replace("\\", "/")
                if self.match_file(rel_path):
                    matching_files.append(os.path.join(root, file))

        return matching_files

    

    
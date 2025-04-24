"""
Installs everything necessary for this package

On linux: install minimal clang compiler from google drive

On windows: install minimal mingw64 compiler from google drive
"""

import subprocess
import os
import pathlib
import platform
import sys
import importlib
import time


def install_certificate(domain_names, email=None, agree_tos=True):
    # Update with new certificate

    install_missing_requirements(
        requirements_file_path=get_directory_path(__file__) + "/requirements.txt",
        other_venv_path=get_directory_path(__file__) + "/venv"
    )

    generate_ssl(domain_names=domain_names, email=email, agree_tos=agree_tos)


def generate_ssl(domain_names, email=None, agree_tos=True):
    if not domain_names:
        print("No domain names provided.")
        sys.exit(1)

    # Build the base command
    cmd = [
        'sudo', sys.executable, '-m', 'certbot',
        'certonly', '--standalone',
        '--non-interactive',
        '--preferred-challenges', 'http'
    ]

    # Email handling
    if email:
        cmd += ['--email', email]
    else:
        cmd += ['--register-unsafely-without-email']

    # TOS agreement
    if agree_tos:
        cmd += ['--agree-tos']

    # Add domain flags
    for domain in domain_names:
        cmd += ['-d', domain]

    try:
        print(f"🔧 Running command:\n{' '.join(cmd)}\n")
        subprocess.check_call(cmd)
        print("✅ SSL Certificate successfully generated.")
    except subprocess.CalledProcessError as e:
        print(f"Error generating certificate: {e}")
        sys.exit(1)


def get_directory_path(__file__in, up_directories=0):
    return str(pathlib.Path(__file__in).parents[up_directories].resolve()).replace("\\", "/")


def run_command(command: str) -> None:
    """Run a command in the terminal"""
    platform_name = platform.system()
    if platform_name == "Windows": # Windows
        print("running command: ", f'powershell; &{command}')
        if command[0] != '"':
            os.system(f'powershell; {command}')
        else:
            os.system(f'powershell; &{command}')
    else:
        print("running command: ", f'{command}')
        os.system(command)


def create_python_virtual_environment(env_directory_path):
    # Setup a python virtual environmet
    os.makedirs(env_directory_path, exist_ok=True) # Ensure directory exists
    run_command(f'"{sys.executable}" -m venv "{env_directory_path}"')


def pip_install_package_in_virtual_environment(env_directory_path, package):
    if not os.path.exists(env_directory_path):
        print("Invalid path")
        raise Exception("Invalid path")
  
    my_os = platform.system()
    if my_os == "Windows":
        run_command(f'"{env_directory_path}/Scripts/pip" install {package}')
    else:
        run_command(f'"{env_directory_path}/bin/pip" install {package}')


def add_other_venv_to_sys_path(other_venv_path):
    def get_site_packages_path(venv_path):
        """Returns the site-packages path for a given virtual environment."""
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        
        # Construct the expected site-packages path
        if os.name == "nt":  # Windows
            site_packages_path = os.path.join(venv_path, "Lib", "site-packages")
        else:  # macOS/Linux
            site_packages_path = os.path.join(venv_path, "lib", python_version, "site-packages")

        return site_packages_path if os.path.exists(site_packages_path) else None

    other_venv_path = get_site_packages_path(other_venv_path)
    if not os.path.exists(other_venv_path):
        raise Exception(f"Path does not exist! {other_venv_path}")

    if not other_venv_path in sys.path:
        sys.path.insert(0, other_venv_path)  # Add other venv's site-packages to sys.path


def try_import_pip_package(package_name):
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False
    

def install_missing_requirements(requirements_file_path, other_venv_path):
    # Step1: Get which packages are missing
    if not os.path.exists(requirements_file_path):
        print(f"Requirements file not found: {requirements_file_path}")
        return
    
    missing_requirements = list()
    with open(requirements_file_path, "r") as f:
        for line in f:
            # Skip comments and empty lines
            if not line:
                continue

            line = line.split("#")[0]
            line = line.strip()
            
            if not line:
                continue

            # Extract just the package name for import checking
            package_name = line.split("==")[0].strip()
            if not try_import_pip_package(package_name=package_name):
                missing_requirements.append(line)


    if len(missing_requirements) == 0:
        return # No missing requirements
    

    # Step2: Create a python virtual environment
    create_python_virtual_environment(other_venv_path)


    # Step3: Install missing packages to the virtual environment
    for package in missing_requirements:
        pip_install_package_in_virtual_environment(
            env_directory_path=other_venv_path,
            package=package
        )

    # Step4: Add virtual enviroment to path
    add_other_venv_to_sys_path(other_venv_path=other_venv_path)


def delete_file(file: str):
    if os.path.exists(file):
        os.remove(file)


if __name__ == "__main__":
    """
    Installs a new certificate for your domain
    Note! You need to make sure the dns points to this ip
    """
    domains = ["vicmil.uk"]

    run_command("sudo systemctl stop nginx")
    time.sleep(3)
    install_certificate(domain_names=domains)
    run_command("sudo systemctl restart nginx")

    # The certificates are stored under: /etc/letsencrypt/live/<your-domain>/
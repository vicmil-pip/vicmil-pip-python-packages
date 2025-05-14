import sys, pathlib, json
sys.path.append(str(pathlib.Path(__file__).resolve().parents[0]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))

import vicmil_pip.packages.pyUtil as pyUtil

pip_manager = pyUtil.PipManager()
pip_manager.add_module("werkzeug", "werkzeug")
pip_manager.include_other_venv()
pip_manager.install_missing_modules()

import random
import string
from werkzeug.security import check_password_hash, generate_password_hash

def generate_password(length=12, use_upper=True, use_digits=True, use_symbols=True):
    if length < 4:
        raise ValueError("Password length should be at least 4")

    # Base characters
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase if use_upper else ''
    digits = string.digits if use_digits else ''
    symbols = string.punctuation if use_symbols else ''

    all_chars = lower + upper + digits + symbols

    if not all_chars:
        raise ValueError("No character sets selected")

    # Guarantee at least one character from each selected set
    password = [
        random.choice(lower),
        random.choice(upper) if use_upper else '',
        random.choice(digits) if use_digits else '',
        random.choice(symbols) if use_symbols else ''
    ]

    # Fill the rest
    password += [random.choice(all_chars) for _ in range(length - len(password))]

    # Shuffle the result
    random.shuffle(password)

    return ''.join(password)

# Example usage
if __name__ == "__main__":
    pwd = "123"
    # pwd = generate_password(length=16, use_symbols=False)
    print("Generated password:", pwd)
    print("Generated password hash: '" + generate_password_hash(pwd) + "'")

# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Any

try:
    from cryptography.fernet import Fernet
except ImportError:
    raise RuntimeError("Dependencies not installed properly. Run python -m pip install -r requirements.txt.")

import dotenv
import argparse
import logging
import os
import subprocess
import multiprocessing
import sys

dotenv.load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)

_log = logging.getLogger(__name__)

def _check_frontend_present() -> bool:
    _log.info("Checking frontend presence...")

    if os.path.exists("frontend") and os.path.isdir("frontend") and os.path.isfile("frontend/package.json"):
        return True
    
    _log.error("Frontend was not downloaded. Please clone the repository again using --recurse-submodules option set.")
    return False


def _check_node_installation() -> bool:
    _log.info("Checking Node.js installation...")

    process = subprocess.Popen(["node", "-v"], shell=True, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if stderr:
        _log.error("Node.js does not seem to be installed. Please install it first: https://nodejs.org/en/download")
        return False

    parts = stdout.decode().split(".")
    version = int(parts[0].lstrip("v"))

    if version < 22:
        _log.error(f"Node.js 22 or higher is required. {stdout} is not supported. Install the latest version from: https://nodejs.org/en/download")
        return False

    return True

def _check_fernet_key():
    _log.info("Setting up Fernet encryption key...")
    try:
        os.environ["BUJET_ENCRYPTION_KEY"]
    except KeyError:
        _log.info("Fernet encryption key not already set in environment variables. Setting...")
        dotenv_file = dotenv.find_dotenv()

        if dotenv_file:
            _log.info(f"Found environment file at {dotenv_file!r} - adding BUJET_ENCRYPTION_KEY here...")
            dotenv.load_dotenv(dotenv_file)
            dotenv.set_key(dotenv_file, "BUJET_ENCRYPTION_KEY", Fernet.generate_key().decode())
        else:
            _log.info(f"No environment file found. Creating one...")    
            with open(".env", "w") as f:
                f.write(f"BUJET_ENCRYPTION_KEY=\"{Fernet.generate_key().decode()}\"")
            
        _log.info("Fernet encryption key setup successfully.")
    else:
        _log.info("Fernet encryption key already set in environment variables. No operations performed.")


def _install_npm_packages():
    _log.info("Installing NPM packages...")

    process = subprocess.Popen(["cd", "frontend", "&&", "npm", "i", "--production=false"], shell=True, stdout=subprocess.PIPE)
    _, stderr = process.communicate()

    if stderr:
        _log.error("NPM packages installation failed.")
        return False
    
    _log.info("NPM packages installed successfully.")
    return True

def _npm_build():
    _log.info("Building frontend...")

    process = subprocess.Popen(["cd", "frontend", "&&", "npm", "run", "build"], shell=True, stdout=subprocess.PIPE)
    _, stderr = process.communicate()

    if stderr:
        _log.error("Frontend build failed.")
        return False
    
    _log.info("Frontend built successfully.")
    return True

def _exec_command(*args: Any, **kwargs: Any) -> None:
    subprocess.Popen(*args, **kwargs)

def _run_bujet():
    _log.info("Running Bujet...")
    with multiprocessing.Pool(processes=multiprocessing.cpu_count() - 1) as pool:
        _log.info("Starting backend server...")
        pool.apply_async(_exec_command, args=(["fastapi", "run", "app.py"],), kwds={"shell": True})

        _log.info("Starting frontend server...")
        pool.apply_async(_exec_command, args=(["cd", "frontend", "&&", "npm", "run", "start"],), kwds={"shell": True})

        try:
            pool.close()
            pool.join()
        except KeyboardInterrupt:
            pass

def main():
    parser = argparse.ArgumentParser(
        prog="Bujet Automatic Runner",
        description="Convenience execution manager for Bujet",
        epilog="Copyright (C) Izhar Ahmad 2025-2026 - https://github.com/izxxr/bujet",
    )

    parser.add_argument(
        "-I", "--install",
        action="store_true",
        help="Setup Bujet and install essential packagess. This option is only recommended when hosting Bujet locally. " \
             "When deploying to a server, this option must not be used as the installation performed by this method " \
             "is unsafe for such environments. Refer to 'Manual Installation' section in project documentation in such cases. " \
             "As a preventive measure, not passing this option leads to install.py script showing an error."
    )

    args = parser.parse_args()

    if sys.version_info < (3, 9):
        _log.error("Python 3.9 or higher is required. Install latest version from: https://python.org/downloads")
        return

    _check_frontend_present()

    if not _check_node_installation():
        return

    if args.install:
        _log.info(
            "Automatic installation is not recommended for deployments. If you are hosting Bujet locally " \
            "on your machine, you can proceed with this option (enter Y). If you are deploying Bujet on " \
            "a server, please refer to 'Manual Installation' section at project's documentation"
        )
        choice = ""

        while choice.lower() not in ("y", "n"):
            choice = input("Proceed with installation? (Y/n) ")

        if choice == "n":
            _log.info("Installation aborted.")

        _check_fernet_key()

        if not _install_npm_packages():
            return
        
        if not _npm_build():
            return

        _log.info("Installation successful. You can now run Bujet by running python autorun.py")
    else:
        _run_bujet()

if __name__ == "__main__":
    main()

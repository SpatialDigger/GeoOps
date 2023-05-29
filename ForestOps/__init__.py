import subprocess
import warnings


def check_newer_version(package_name, current_version):
    try:
        output = subprocess.check_output(['pip', 'list', '--outdated'])
        packages = output.decode().strip().split('\n')[2:]
        for package in packages:
            name, *other_info = package.split()
            version = other_info[0]
            if name.lower() == package_name.lower() and version > current_version:
                return True
    except subprocess.CalledProcessError:
        pass

    return False


def _warn_if_newer_version_available():
    package_name = 'ForestOps'
    current_version = '0.1.0'

    if check_newer_version(package_name, current_version):
        warning_message = f"A newer version of {package_name} is available. Please consider upgrading."
    else:
        warning_message = f"This is the latest version of {package_name}. Beware it is under development, please report any bugs."

    warnings.warn(warning_message, UserWarning)


_warn_if_newer_version_available()


from .geo_ops import *
from .stats import *
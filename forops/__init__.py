from .geo_ops import *
from .stats import *

import subprocess
import warnings


def check_newer_version(package_name, current_version):
    try:
        output = subprocess.check_output(['pip', 'list', '--outdated'])
        packages = output.decode().strip().split('\n')[2:]
        for package in packages:
            name, version, _ = package.split()
            if name.lower() == package_name.lower() and version > current_version:
                return True
    except subprocess.CalledProcessError:
        pass

    return False


package_name = 'forops'
current_version = '0.0.5'

if check_newer_version(package_name, current_version):
    warning_message = f"A newer version of {package_name} is available. Please consider upgrading."
    warnings.warn(warning_message, UserWarning)
else:
    warning_message = f"This is the current version of {package_name}, beware it is in development."
    warnings.warn(warning_message, UserWarning)

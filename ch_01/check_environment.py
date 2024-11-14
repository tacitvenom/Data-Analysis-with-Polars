"""Check environment for following along with the text."""

from packaging.version import Version
from distutils.version import LooseVersion as PythonVersion

import importlib
import sys
import toml


OK = '\x1b[42m[ OK ]\x1b[0m'
FAIL = '\x1b[41m[FAIL]\x1b[0m'

def run_checks(raise_exc=False):
    """
    Check that the packages we need are installed and the Python version is good.

    Parameters
    ----------
    raise_exc : bool, default ``False``
        Whether to raise an exception if any of the packages doesn't
        match the requirements (used for GitHub Action).
    """
    failures = []

    with open('../pyproject.toml', 'r') as file:
        pyproject = toml.load(file)

    # check Python version
    python_version_limits = pyproject['project']['requires-python']
    is_python_version_okay = True
    for python_version_limit in python_version_limits.split(", "):
        current_python_version = Version(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        if ">=" in python_version_limit:
            if not (current_python_version >= Version(python_version_limit.split(">=")[-1])):
                is_python_version_okay = False
                break;
        elif ">" in python_version_limit:
            if not (current_python_version > Version(python_version_limit.split(">")[-1])):
                is_python_version_okay = False
                break;
        elif "<=" in python_version_limit:
            if not (current_python_version <= Version(python_version_limit.split("<=")[-1])):
                is_python_version_okay = False
                break;
        elif "<" in python_version_limit:
            if not (current_python_version < Version((python_version_limit.split("<")[-1]))):
                is_python_version_okay = False
                break;
        elif "==" in python_version_limit:
            if not (current_python_version == Version(python_version_limit.split("==")[-1])):
                is_python_version_okay = False
                break;

    if is_python_version_okay:
        print(OK, 'Python is version %s\n' % sys.version)
    else:
        print(FAIL, f'Python version {python_version_limits} is required, but {sys.version} is installed.')
        failures.append('Python')

    # read in the requirements
    dependencies = pyproject['project']['dependencies']
    sources = pyproject['tool']['uv']['sources']
    requirements = dict()
    for dependency in dependencies:
        if dependency in sources.keys():
            pkg = dependency.replace('-', '_')
            version = None
        else:
            pkg, version = dependency.split('>=')
            if pkg == 'imbalanced-learn':
                pkg = 'imblearn'
            elif pkg == 'scikit-learn':
                pkg = 'sklearn'    

        requirements[pkg.replace('-', '_')] = version

    # check the requirements
    for pkg, req_version in requirements.items():
        try:
            mod = importlib.import_module(pkg)
            if req_version:
                version = mod.__version__
                if not Version(version) >= Version(req_version):
                    print(FAIL, '%s version %s is required, but %s installed.' % (pkg, req_version, version))
                    failures.append(pkg)
                    continue
            print(OK, '%s' % pkg)
        except ImportError:
            print(FAIL, '%s not installed.' % pkg)
            failures.append(pkg)

    if failures and raise_exc:
        raise Exception(
            'Environment failed inspection due to incorrect versions '
            f'of {len(failures)} item(s): {", ".join(failures)}.'
        )

if __name__ == '__main__':
    run_checks(raise_exc=True)

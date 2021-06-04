from setuptools import setup, find_packages
from pathlib import Path

PACKAGE_NAME = 'magnanimus'

# make a project data dir and log dir
base_dir = Path(f'~/.{PACKAGE_NAME}').expanduser()

if not base_dir.exists():
    base_dir.mkdir()
    for subdir in ['logs', 'data', 'config']:
        (base_dir / subdir).mkdir()


setup(
    name=PACKAGE_NAME, # will come up this way eg in pip list, but
                       # import name is from packages field below
                       # i.e. the folder name
    version='0.0.1',

    # sets the root dir for finding packages as src
    package_dir = {'': 'src'},

    # find all packages in passed dir
    packages = find_packages('src'),

    # or can do it manually with a list (of folders, not files)
    # (it is fine to install multiple packages - both will be available
    #  to import, though pip will only know the name above)
    # packages=['my_package', 'another_package'],

    # Sets up cli commands: in this case $ my_package-cli
    # Use dot notation (__init__.py not necessary)
    # Must point to a function (after the ':')
    # Standard is to use a __main__.py module which allows
    # $ python -m my_package

    # entry_points = {
    # 'console_scripts': [
    #     f'{PACKAGE_NAME}-cli = {PACKAGE_NAME}.__main__:main',
    # ]},

    # alternative to entry_points, this makes the script available
    # in cli (need to give full file name, and alias elsewhere if reqd)
    # Not preferred
    # scripts=['bin/my_script.py'],

    # to add package_data - if distributing
    # package_data={'capitalize': ['data/cap_data.txt']},

    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],  # Optional
)

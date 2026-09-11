from distutils.command.install_scripts import install_scripts
from gettext import install
import setuptools

setuptools.setup(
    name = "IDPsych",
    version = "1.1.1",
    author = "LW",
    author_email = "laiwei@uchicago.edu",
    description = "Analyze the IDPsych data",
    url = "https://bitbucket.org/kylelevii/final_project/src/master/",
    packages = setuptools.find_packages(),
    install_requires = [
        'numpy',
        'scipy',
        'matplotlib',
        'seaborn',
        'pymatreader',
        'statistics',
        ],
)
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize

include_dirs = ['.']

setup(
    name="server",
    ext_modules=cythonize([
        Extension(name="server",
            sources=["main.pyx"],
            include_dirs=include_dirs
        )
    ]),
    zip_safe=False
)
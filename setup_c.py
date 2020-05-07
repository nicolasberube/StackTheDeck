#Compile first with python setup_c.py build_ext --inplace

from setuptools import setup, Extension
#from setuptools.command.build_py import build_py

ext_modules = []
ext_modules.append(Extension("holes_operations",
  ["holes_operations.c"],
  extra_compile_args=['-O3']
  ))

setup(
    ext_modules=ext_modules,
#    cmdclass={"build_py": build_py},
)

#Compile first with python so_setup.py build_ext --inplace
#File might need to be renamed to holes_operations.so

from setuptools import setup, Extension
#from setuptools.command.build_py import build_py

ext_modules = []
ext_modules.append(Extension("holes_operations",
  ["holes_operations_mac.c"],
  extra_compile_args=['-O3']
  ))

setup(
    ext_modules=ext_modules,
#    cmdclass={"build_py": build_py},
)

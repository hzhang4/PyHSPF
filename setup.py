import os, sys, glob, subprocess
import shutil

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from pathlib import Path

ext_name = 'hspf'
hspf_dir = 'src/hspf13'

class f2py_Build(build_ext):
    def run(self):
        ext_files = glob.glob(f'{hspf_dir}/*.c') + glob.glob(f'{hspf_dir}/*.f')
        if not ext_files:
            print(f"No HSPF source files (.f, .c) found in {hspf_dir}!")
            return
        
        # Convert all paths to use forward slashes
        include_dir = str(Path(hspf_dir).resolve().as_posix())
        ext_files = [str(Path(f).as_posix()) for f in ext_files]

        cmd = [
            sys.executable, '-m', 'numpy.f2py',
            '-c',  # compile
            '-m', ext_name,  # module name
            '--backend', 'meson',
            '--opt=-static',
            '--f77flags=-O3 -fno-automatic -fno-align-commons -fallow-argument-mismatch -std=legacy -I' + include_dir,
        ] + ext_files

        try:
            result = subprocess.run(cmd, check=True)
            print("Build completed successfully!")

            built_files = glob.glob(f'{ext_name}*.pyd') + glob.glob(f'{ext_name}*.so')
            if not built_files:
                print(f"No built files found for {ext_name}!")
                return
            
            for built_file in built_files:
                shutil.copy2(built_file, self.build_lib)

        except subprocess.CalledProcessError as e:
            print(f"Build failed with return code: {e.returncode}")
            print(f"F2PY Command: {' '.join(cmd)}...")
            if e.stdout:
                print("STDOUT:", e.stdout[-1500:])  # Show more output
            if e.stderr:
                print("STDERR:", e.stderr[-1500:])  # Show more error details
            return False
    
if __name__ == "__main__":
    setup(
        cmdclass={'build_ext': f2py_Build},
        ext_modules=[Extension(ext_name, [])],
    )
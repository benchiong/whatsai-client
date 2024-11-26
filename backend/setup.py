from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {
    'packages': [],
    'excludes': [],
    "include_files": [
    ],
}

base = 'service'

executables = [
    Executable('main.py', base=base, target_name = 'py-backend')
]

setup(name='whatsai-client',
      version = '0.0.1-alpha0',
      description = 'backend of whatsai',
      options = {'build_exe': build_options},
      executables = executables)

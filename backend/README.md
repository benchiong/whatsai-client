package it use pyinstaller:

  1.change backend.misc.options env to 'prod' (log files are in base_dir/log dir)

  2.pyinstaller --onefile .\main.py; if you use main.spec file to package, remember edit the path to right

  3.find main.exe in backend/dist

  4.copy to frontend/app/main.exe, for following electron package work.

  5.copy backend/comfy dir to base_dir, rename it to comfy_outer(for dynamic loading, 
    after pyinstaller package the program, it will lose dynamic ability to load
    files with import module).
    

  Base_dir will differ for different OS, D://whatsai for windows
    ~/whatsai for macOS



Debug:
fastapi:
http://127.0.0.1:8172/docs (8172 is the port you set in misc/argparser.py)

build:
remove dist , build dirs and  main.spec file, use --clean, try and see
    - pyinstaller --clean --onefile .\main.py 
    if you need more info, add --log-level DEBUG:
      pyinstaller --onefile --clean --log-level DEBUG .\main.py

issues I know:
 - do not install jupyter related in venv, keep as clean as possible, if not work delete the whole venv
   and reinstall from beginning
 - use dist/main.exe instead of build/main/main.exe, which made me paid a lot of times there
 - (Unsolved yet)
    82015 WARNING: Library not found: could not resolve 'avdevice-58.dll', dependency of 'D:\\Projects\\whatsai-client\\backend\\.venv\\Lib\\site-packages\\torio\\lib\\_torio_ffmpeg4.pyd'.
 

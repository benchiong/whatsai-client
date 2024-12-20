The frontend with Electron + NextJs, by Nextron

when package:

1.put the python backend-manager to frontend/assets/backend-manager

2.package them all to a whole app, with:
   nextron build


How Backend Manager works:

1. It's a exe file packaged using python pyinstaller, look backend-manager for detail;
2. When electron starts, it will check backend-manager file, then start a progress to execute it and 
   monitor it to restart if it failed;
3. Backend manager will focus on if the python env is ready, requirements of python, and the backend source code,
   and try to start backend if it fails;
4. When the app quits, it will make sure backend manager before quit.
5. After the process starts and set backend manager url frontend can talk with backend manager 
   through BackendManagerProvider, look renderer/providers/BackendManagerProvider.tsx for detail.
6. if you want to debug, look main/debug.ts for detail.

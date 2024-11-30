import path from "path";
import { app, BrowserWindow, ipcMain, Menu } from "electron";
import serve from "electron-serve";
import { createWindow } from "./helpers";
import { execFile } from "child_process";
import fs from 'fs';
import { ChildProcess } from "node:child_process";
import treeKill from "tree-kill";
import { RecoilLoadable } from "recoil";


const isProd = process.env.NODE_ENV === "production";

if (isProd) {
  serve({directory: "app"});
} else {
  app.setPath("userData", `${app.getPath("userData")} (development)`);
}

const create_main_window = async () => {
  const options = {
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  };
  
  const mainWindow = createWindow("main", options);
  if (isProd) {
    await mainWindow.loadURL("app://./home");
  } else {
    const port = process.argv[2];
    await mainWindow.loadURL(`http://localhost:${port}/home`);
    mainWindow.webContents.openDevTools();
  }
  return mainWindow;
};

let pythonBackend: ChildProcess | null = null;

(async () => {
  await app.whenReady();
  await create_main_window();
})();

// https://stackoverflow.com/questions/67146654/how-to-compile-python-electron-js-into-desktop-app-exe
(async () => {
  // if (isProd) {
  
  if (pythonBackend) {
    console.log('Python backend is already running.');
    return
  }
  
  const pythonExePath = path.join(__dirname, "main.exe")
  console.log(__dirname)
  
  fs.access(pythonExePath, fs.constants.F_OK, (err) => {
    if (err) {
      console.error('Python exe file not exits.');
    } else {
      pythonBackend = execFile(
        pythonExePath,
        [],
        (error, stdout, stderr) => {
          if (error) {
            console.error(`Python error: ${error.message}`);
            return
          }
          
          console.log(`Python stdout: ${stdout}`);
          console.error(`Python stderr: ${stderr}`)
          
        });
      
      console.log("pythonBackend started")
      
    }
  });
  // }
})();

function cleanUp() {
  console.log("Cleaning up before quit");
  if (pythonBackend && pythonBackend.pid) {
    treeKill(pythonBackend.pid, 'SIGTERM', (err) => {
      if (err) {
        console.error(err);
      }
    });
    console.log("Python backend stopped");
  }
}

app.on('before-quit', (event) => {
  console.log('App is about to quit');
  cleanUp();
});


app.on('will-quit', () => {
  console.log('App is quitting');
  cleanUp();
});

app.on('quit', () => {
  console.log('App has quit');
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
    if (pythonBackend) {
      pythonBackend.kill()
    }
  }
});


app.on("activate", async () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    await create_main_window();
  }
});

ipcMain.on("message", async (event, arg) => {
  event.reply("message", `${arg} World!`);
});

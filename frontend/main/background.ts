import path from "path";
import { app, BrowserWindow, ipcMain } from "electron";
import serve from "electron-serve";
import { createWindow } from "./helpers";
const { spawn } = require("child_process");

const isProd = process.env.NODE_ENV === "production";

if (isProd) {
  serve({ directory: "app" });
} else {
  app.setPath("userData", `${app.getPath("userData")} (development)`);
}

(async () => {
  await app.whenReady();
  await create_main_window();

  // // https://stackoverflow.com/questions/67146654/how-to-compile-python-electron-js-into-desktop-app-exe
  // const pythonExePath = path.join(__dirname, "python-backend-exe");
  // var python = require("child_process").execFile(pythonExePath);
  // console.log("start python");

  const pythonExePath = path.join(__dirname, "python-backend-exe");
  const pythonProcess = spawn(pythonExePath);

  pythonProcess.stdout.on("data", (data) => {
    console.log(`stdout: ${data}`);
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error(`stderr: ${data}`);
  });

  pythonProcess.on("close", (code) => {
    console.log(`child process exited with code ${code}`);
  });
})();

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

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", async () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    await create_main_window();
  }
});

ipcMain.on("message", async (event, arg) => {
  event.reply("message", `${arg} World!`);
});

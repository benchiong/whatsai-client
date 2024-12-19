import path from "path";
import { app, BrowserWindow, ipcMain } from "electron";
import serve from "electron-serve";
import { createWindow } from "./helpers";
import { BackendManager } from "./backend-manager";

const isProd = process.env.NODE_ENV === "production";

if (isProd) {
  serve({ directory: "app" });
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

(async () => {
  await app.whenReady();
  await create_main_window();
})();

let backendManager: BackendManager | null = null;
(async () => {
  if (!isProd) {
    console.log("Dev env found, manually start backend please.");
    return;
  }
  const pythonExePath = path.join(__dirname, "backend-manager");
  backendManager = new BackendManager(pythonExePath);
  await backendManager.startProcess();
})();

let stopping = false;
app.on("before-quit", (event) => {
  if (!stopping && isProd) {
    stopping = true;
    event.preventDefault();
    if (backendManager) {
      try {
        backendManager.stopProcess().then(() => {
          console.log("before-quit stoprocess");
          app.quit();
        });
      } catch (e) {
        console.error("stopPythonBackendManager failed:", e);
        app.quit();
      }
    }
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
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

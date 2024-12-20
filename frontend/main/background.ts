import path from "path";
import { app, BrowserWindow, ipcMain } from "electron";
import serve from "electron-serve";
import { createWindow } from "./helpers";
import { BackendManager } from "./backend-manager";
import { debug_backend, debug_manager } from "./debug";

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
  if (debug_manager || debug_backend) {
    return;
  }

  const pythonExePath = app.isPackaged
    ? path.join(process.resourcesPath, "assets", "backend-manager")
    : path.join(__dirname, "../assets", "backend-manager");

  console.log(pythonExePath);

  backendManager = new BackendManager(pythonExePath);
  await backendManager.startProcess();
})();

let stopping = false;
app.on("before-quit", (event) => {
  if (debug_manager || debug_backend) {
    return;
  }

  if (!stopping) {
    stopping = true;
    event.preventDefault();

    if (backendManager) {
      try {
        backendManager.stopProcess().then(() => {
          console.log("before-quit stop process.");
          app.quit();
        });
      } catch (e) {
        console.error("Stop Python Backend Manager failed:", e);
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

// demo code from nextron, leave here in case I forget how to write it, how idiot am I....
ipcMain.on("message", async (event, arg) => {
  event.reply("message", `${arg} World!`);
});

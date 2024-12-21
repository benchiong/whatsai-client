import { spawn, ChildProcess } from "child_process";
import * as net from "net";
import fs from "fs";
import { ipcMain } from "electron";
import { backendManager } from "./ipc-constants";
import { eventBackendManagerUrl } from "./ipc-constants";
import { debug_manager, debug_manager_url } from "./debug";

export let managerUrl = null;
if (debug_manager) {
  managerUrl = debug_manager_url;
}
export class BackendManager {
  private process: ChildProcess | null = null;
  private readonly executablePath: string;
  private monitor = false;
  private port = null;

  constructor(executablePath: string) {
    this.executablePath = executablePath;
  }

  public async startProcess(): Promise<void> {
    if (this.process) {
      console.log("Process is already running.");
      return;
    }

    fs.access(this.executablePath, fs.constants.F_OK, (err) => {
      if (err) {
        console.error("Python exe file not exits.");
        return;
      }

      this.findAvailablePort(8820).then((port) => {
        if (!port) {
          console.error("Can't find available port");
          return;
        }
        this.port = port;

        console.log("Port", this.port, "executablePath:", this.executablePath);

        this.process = spawn(
          this.executablePath,
          ["--port", this.port.toString(), "--prod"],
          {
            stdio: "inherit",
          },
        );
        this.monitor = true;

        if (this.port) {
          managerUrl = this.managerUrl();
        }

        this.process.on("exit", (code) => {
          console.log(`Process exited with code: ${code}`);

          if (code !== 0 && this.monitor) {
            console.log("Process crashed. Restarting...");
            this.startProcess();
          }
        });

        this.process.on("error", (err) => {
          console.error("Failed to start process:", err);
          if (this.monitor) {
            this.startProcess();
          }
        });
      });
    });
  }
  public async stopProcess(): Promise<void> {
    if (this.process) {
      const managerServerUrl = this.managerUrl();
      const killSelfUrl = `${managerServerUrl}process/kill_self`;
      console.log("killSelfUrl:", killSelfUrl);

      if (!killSelfUrl) {
        console.log("empty killSelfUrl");
        return;
      }

      console.log("Stopping process...");
      this.monitor = false;

      try {
        await fetch(killSelfUrl, {
          method: "GET",
        });
      } catch (e) {
        console.log("Python backend manager kill self failed:", e);
      }
    } else {
      console.log("No process to stop.");
    }
  }

  public managerUrl(): string | null {
    if (this.port) {
      return `http://127.0.0.1:${this.port}/`;
    }
    return null;
  }

  private isPortOccupied(port: number): Promise<boolean> {
    return new Promise((resolve, reject) => {
      const server = net.createServer();

      server.once("error", (err: NodeJS.ErrnoException) => {
        if (err.code === "EADDRINUSE") {
          resolve(true);
        } else {
          reject(err);
        }
      });

      server.once("listening", () => {
        server.close();
        resolve(false);
      });

      server.listen(port, "127.0.0.1", () => {
        server.close();
      });
    });
  }

  private async findAvailablePort(startPort: number): Promise<number | null> {
    let port = startPort;

    while (true) {
      const occupied = await this.isPortOccupied(port);
      if (!occupied) {
        return port;
      }

      port += 1;
      if (port > 65535) {
        return null;
      }
    }
  }
}

ipcMain.on(backendManager, async (event, event_type: string) => {
  if (event_type == eventBackendManagerUrl) {
    event.reply(backendManager, managerUrl);
    console.log("IPC main:", managerUrl);
  }
});

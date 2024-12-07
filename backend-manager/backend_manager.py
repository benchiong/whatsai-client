import asyncio
import subprocess


class AsyncProcessManager:
    def __init__(self, command):
        self.command = command
        self.process = None
        self.monitor = False
        self.port = None

    async def start_process(self):
        print(f"Starting process: {self.command}")
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False
        )
        print(f"Backend started. command: {self.command}")

    async def monitor_process(self):
        self.monitor = True
        print("Begin to monitor process")
        while True and self.monitor:
            if self.process is None or self.process.returncode is not None:
                print(f"Process stopped. Restarting...")
                await self.start_process()
            await asyncio.sleep(5)

    async def stop_process(self):
        self.monitor = False
        if self.process:
            try:
                print(f"Stopping process: PID={self.process.pid}")
                self.process.terminate()
                await self.process.wait()
                self.process = None
            except Exception as e:
                print("stop_process error:", e)

    async def read_output(self):
        if self.process:
            stdout, stderr = await self.process.communicate()
            print(f"Process output: {stdout}")
            if stderr:
                print(f"Process error: {stderr}")


manager: AsyncProcessManager | None = None



import asyncio
import subprocess
from logger import logger


class AsyncProcessManager:
    def __init__(self, command):
        self.command = command
        self.process = None
        self.monitor = False
        self.port = None

    async def start_process(self):
        logger.info(f"Starting process: {self.command}")
        self.process = await asyncio.create_subprocess_exec(
            *self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False
        )
        logger.info(f"Backend started. command: {self.command}")
        logger.info(f"AsyncProcessManager.process: {self.process}")


    async def monitor_process(self):
        self.monitor = True
        logger.info("Begin to monitor process")
        while True and self.monitor:
            if self.process is None or self.process.returncode is not None:
                logger.info(f"Process stopped. Restarting...")
                await self.start_process()
            await asyncio.sleep(5)

    async def stop_process(self):
        self.monitor = False
        if self.process:
            try:
                logger.info(f"Stopping process: PID={self.process.pid}")
                self.process.terminate()
                await self.process.wait()
                self.process = None
            except Exception as e:
                logger.info("stop_process error:", e)

    async def read_output(self):
        if self.process:
            stdout, stderr = await self.process.communicate()
            logger.info(f"Process output: {stdout}")
            if stderr:
                logger.info(f"Process error: {stderr}")


manager: AsyncProcessManager | None = None



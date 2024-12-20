import os
import signal

import psutil

from logger import logger
from fastapi import APIRouter, HTTPException

import backend_manager
router = APIRouter()

@router.get('/kill_process_by_name')
async def kill_process_by_name(process_name: str):
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == process_name.lower():
            logger.info(proc.info)
            pid = proc.info.get('pid', None)
            try:
                process = psutil.Process(pid)
                process.terminate()
                pids.append(pid)
            except psutil.NoSuchProcess:
                raise HTTPException(status_code=404, detail="Process not found")
            except PermissionError:
                raise HTTPException(status_code=403, detail="Permission denied")
    return pids

@router.get('/kill_self')
async def kill_self():
    if backend_manager.manager:
        await backend_manager.manager.stop_process()
    else:
        logger.info(f"No manager found.")

    # Warning got:
    # /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/multiprocessing/resource_tracker.py:254:
    # UserWarning: resource_tracker: There appear to be 8 leaked semaphore objects to clean up at shutdown
    # find why and fix
    # reproduce: start manager server and click：
        # http://127.0.0.1:8820/docs#/default/kill_self_process_kill_self_get
    #todo: it seems there are leaked issues here:

    pid = os.getpid()
    ppid = os.getppid()
    os.kill(pid, signal.SIGTERM)
    os.kill(ppid, signal.SIGTERM)

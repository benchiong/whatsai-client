Backend of whatsAI Client, real worker of project, includes comfy, model downloader, prompt worker
It's a fastapi server, the codes will be downloaded by backend-manager and then start it;

-core: the core concepts of WhatsAI are here, look the codes will get most explanation;
-DB is sqlite, it combines with pydantic, see data_type for details, synchronous and should be thread safe;
-prompt worker: generation work done here, it's a separate thread, fully with Comfy and WhatsAI's core logics;
-model_download_worker: a separate thread, sync CivitAI model info by sha_256, and download model on CivitAI.
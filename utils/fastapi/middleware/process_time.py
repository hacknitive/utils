from time import time

from fastapi import FastAPI, Request


def prepare_process_time_header(
        app: FastAPI,
):
    @app.middleware("http")
    async def add_process_time_header(
            request: Request,
            call_next,
    ):
        start_time = time()
        response = await call_next(request)
        response.headers["X-Process-Time"] = str(round(time() - start_time, 4))
        return response

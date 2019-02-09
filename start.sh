#!/bin/bash
uvicorn src.app.api:app --host 0.0.0.0 --port ${PORT}
# gunicorn -w 2 -k uvicorn.workers.UvicornWorker --log-level warning src.app.api:app --bind 0.0.0.0:${PORT}
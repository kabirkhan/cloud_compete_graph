#!/bin/bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker --log-level warning app.api:app
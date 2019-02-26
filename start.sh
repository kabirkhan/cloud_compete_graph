#!/bin/bash
uvicorn src.app.api:app --host 0.0.0.0 --port ${PORT}
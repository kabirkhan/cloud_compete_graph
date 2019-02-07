#!/bin/bash
uvicorn src.app.api:app --port ${PORT}
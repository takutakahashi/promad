#!/bin/bash

if [[ "$RULES_PATH" = "" ]]; then
    echo "env RULES_PATH is not defined. ex: /path/to/rules.yaml"
    exit 1
fi

if [[ "$PROM_API_URL" = "" ]]; then
    echo "env PROM_API_URL is not defined. ex: http://localhost:9090/api/v1"
    exit 1
fi

exec uvicorn main:app --host 0.0.0.0 --port 9400
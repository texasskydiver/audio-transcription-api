#!/bin/sh
printenv

echo "PORT is: $PORT"
if [ -z "$PORT" ]; then
  echo "PORT environment variable is not set!"
  exit 1
fi
exec uvicorn main:app --host 0.0.0.0 --port $PORT 
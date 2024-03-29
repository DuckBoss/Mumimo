#!/usr/bin/bash

cd "${0%/*}"
cd ..

ENV_FILE=".config/.env"
LOG_DIR=".config/logs/"

echo "Running Mumimo..."
./mumimo.py -v "--env-file=$ENV_FILE" "--config-file=.config/config.toml" "--log-config-file=.config/logging.toml" $@

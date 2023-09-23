#!/usr/bin/env bash -e

clear
cd "${0%/*}"
cd ..

DB_FILE=".config/mumimo.sqlite"
PLUGIN_CONFIG_DIR=".config/plugins"
ENV_FILE=".config/.env"
LOG_DIR=".config/logs/"


echo "Removing old logs..."
rm -rf "$LOG_DIR"
if [ $? -ne 0 ] ; then
    echo "Encountered an error removing old logs."
else
    echo "Removed '$LOG_DIR'"
fi


echo "Removing old databases..."
if [ -f "$DB_FILE" ] ; then
    rm "$DB_FILE"
    if [ $? -ne 0 ] ; then
        echo "Encountered an error removing the old database."
    else
        echo "Removed '$DB_FILE'"
    fi
fi

echo "Removing plugin config folder.."
rm -r "$PLUGIN_CONFIG_DIR"
if [ $? -ne 0 ] ; then
    echo "Encountered an error removing the plugin config folder."
else
    echo "Removed '$PLUGIN_CONFIG_DIR'"
fi

# Thanks to V.Gamula/Gulzar on stackoverflow for this convenient command:
# https://stackoverflow.com/questions/28991015/python3-project-remove-pycache-folders-and-pyc-files
echo "Removing pycache files..."
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
if [ $? -ne 0 ] ; then
    echo "Encountered an error removing the plugin config folder."
else
    echo "Removed pycache files."
fi


echo "Running Mumimo with arguments: '$@'"
echo "==================================="
python3.9 ./mumimo.py "-vv" "--env-file=$ENV_FILE" "--config-file=.config/config.toml" "--log-config-file=.config/logging.toml" $@

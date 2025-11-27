# The main Terminal will eventually run the Hot Reloading

# Start Up Shell
osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down'
osascript -e 'tell application "Terminal" to do script "code ." in front window'


#!/bin/bash

# Define the folder to watch
WATCH_FOLDER_TEMPLATES="$(pwd)/flask_commands/templates"
WATCH_FOLDER_COMMANDS="$(pwd)/flask_commands/commands"
WATCH_FOLDER_UTILS="$(pwd)/utils.py"


# Watch for file changes in the folder and its subfolders
refresh_package() {
    # Run pip install -e . in the front Terminal window (project dir expanded)
    osascript -e 'tell application "Terminal" to do script "pip3 install -e ." in front window'
}

# Use null-delimited output from fswatch and add a small debounce to avoid
# running installs for every rapid save.
MIN_INTERVAL=2
last_run=0
fswatch -0 "$WATCH_FOLDER_TEMPLATES" "$WATCH_FOLDER_COMMANDS" "$WATCH_FOLDER_UTILS" | while IFS= read -r -d '' event; do
    echo "Change detected: $event"
    now=$(date +%s)
    if (( now - last_run < MIN_INTERVAL )); then
        echo "Skipping (debounced)"
        continue
    fi
    last_run=$now
    refresh_package
done

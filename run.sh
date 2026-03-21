osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down'
osascript -e 'tell application "Terminal" to do script "pipx install --editable ." in front window'
osascript -e 'tell application "Terminal" to do script "code ." in front window'
osascript -e 'tell application "Terminal" to do script "poetry run sphinx-autobuild -a -E -W -n -b html docs/source docs/build/html" in front window'

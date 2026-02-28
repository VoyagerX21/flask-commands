osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down'
osascript -e 'tell application "Terminal" to do script "pip3 install -e ." in front window'
osascript -e 'tell application "Terminal" to do script "code ." in front window'
osascript -e 'tell application "Terminal" to do script "poetry run sphinx-autobuild -W -n -b html docs/source docs/build/html" in front window'

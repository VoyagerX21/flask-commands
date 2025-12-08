osascript -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down'
osascript -e 'tell application "Terminal" to do script "pip3 install -e ." in front window'
osascript -e 'tell application "Terminal" to do script "code ." in front window'

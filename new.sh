python3 generate.py > html/table.html
cat html/start.html html/table.html html/end.html > cleaning_duty.html
google-chrome --headless --screenshot --window-size=1800,800 --default-background-color=0 cleaning_duty.html
eog screenshot.png

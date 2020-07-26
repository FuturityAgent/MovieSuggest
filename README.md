### Description
Simple app, which recommends movies for an user
based on last entered positions.
In order to get recommendations, one need to insert at
least 3 last seen movies.

### Installation
1. Clone repository on your device.

2.Install dependencies by running ``` pip install -r requirements.txt  ```, if it won't work, use pip3 instead.

3.Now you need to apply migrations by running ```python manage.py migrate```, or ``` python3 manage.py migrate ```.
This will create a new sqlite3 database in the same directory as manage.py file.

4.Enjoy!

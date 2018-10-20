# lol_rune_matchups

## Installation instructions:

Install python3 (Currently being developed on Python 3.6.6): https://www.python.org/downloads/

Make a folder on your computer to store the application, go to that path in your command prompt.

Run `git clone https://github.com/nwsm/march-insanity.git`

Install requirements: pip install -r requirements.txt

We don't have a remote database yet, so you'll need to create your own and fill it.
1) Run: python db_create.py
2) Run: python get_data.py

To run the application, run: python main.py

The app will now be running at http://localhost:5000

To develop, stop the app, make changes, run main.py again

If you are only do front end development, then doing a Empty Cache and Hard Reset is fine.
from flask import Flask, url_for, jsonify, render_template
from markupsafe import escape
from urllib.request import urlopen
import json
import pandas as pd
from serpapi import GoogleSearch
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv
import csv
from pathlib import Path
import sys

name = "James Pasternak"

# check if file called official-highlights/<name>.json exists
# if it does, stop
# if it doesn't create one

filename = f"official-highlights/{name}.json"
path = Path(filename)

# Check if file exists
if path.exists():
    print("File already exists. Stopping.")
    sys.exit()

else:
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2)

    print(f"Created {filename}")

DATA_FILE = f"official-highlights/{name}.json"

load_dotenv()
params = {
  "api_key": os.getenv("SERPAPI_KEY"),
  "engine": "google",
  "q": f"allintitle: {name}",
  "location": "Toronto, Ontario, Canada",
  "google_domain": "google.ca",
  "gl": "ca",
  "hl": "en",
  "tbm": "nws",
  "num": 2
}

def fetch_api_data():
    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        if "news_results" in results:
            df = pd.json_normalize(results["news_results"])
            df.to_json(DATA_FILE, orient="records", indent=2)
            print("Data saved successfully.")
        else:
            print("No news_results found in API response")

    except Exception as e:
        print("Error fetching API data: " + str(e))

def load_data():
    try:
        return json.load(open(DATA_FILE, "r"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"message": "No data available"}

'''
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_api_data, "interval", days=1)
scheduler.start()
'''

if __name__ == '__main__':
    fetch_api_data()

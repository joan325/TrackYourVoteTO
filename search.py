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

DATA_FILE = "data.json"

load_dotenv()
params = {
  "api_key": os.getenv("SERPAPI_KEY"),
  "engine": "google",
  "q": "Toronto City Council motions",
  "location": "Toronto, Ontario, Canada",
  "google_domain": "google.ca",
  "gl": "ca",
  "hl": "en",
  "tbm": "nws"
}

def fetch_api_data():
    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        if "news_results" in results:
            df = pd.json_normalize(results["news_results"])
            df.to_json(DATA_FILE, orient="records", indent=2)
            print("Data saved successfully to data.json")
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

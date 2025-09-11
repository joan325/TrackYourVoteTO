from flask import Flask, url_for, jsonify, render_template, session, request
from markupsafe import escape
from urllib.request import urlopen
import json
import pandas as pd
from serpapi import GoogleSearch
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv
import csv
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
DATA_FILE = "data.json"

## news articles

load_dotenv()
params = {
  "api_key": os.getenv("SERPAPI_KEY"),
  "engine": "google",
  "q": "\"Toronto City Council\"",
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

def load_data(file_name):
    try:
        return json.load(open(file_name, "r"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"message": "No data available"}

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(load_data(DATA_FILE))

@app.route('/in-the-news', methods=['GET'])
def get_vote_highlights():
    return jsonify(load_data('in_the_news.json'))


scheduler = BackgroundScheduler()
scheduler.add_job(fetch_api_data, "interval", days=1)
scheduler.start()

app.secret_key = os.getenv("SECRET_KEY")

if __name__ == '__main__':
    fetch_api_data()
    app.run(debug=True)

## accessing voting record (motions)
base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/datastore_search"
resource_id = "55ead013-2331-4686-9895-9e8145b94189"
limit = 99000

url = f"{base_url}?resource_id={resource_id}&limit={limit}"
data = urlopen(url)
assert data.code == 200

response_dict = json.loads(data.read())
assert response_dict['success'] is True
result = response_dict['result']

pd.set_option('display.max_columns', None)
vr = pd.json_normalize(result["records"]) # full voting record for 2022-26

# organizing: names and date
vr["Date & Time"] = pd.to_datetime(vr["Date/Time"].str[:16], format="mixed", yearfirst=True)
vr["Full name"] = vr["First Name"] + " " + vr["Last Name"]
vr = vr[["Full name", "Agenda Item Title", "Date & Time", "Vote", "Result", "Agenda Item #", "Motion Type", "Vote Description"]]
vr = vr.iloc[::-1]


# filter for motion list
motions_all = vr[["Agenda Item Title", "Result", "Date & Time", "Agenda Item #", "Motion Type", "Vote Description"]].drop_duplicates()

## accessing elected officials info
resource_id = "16d6b1b3-b474-47f4-8c09-8bf5b3aa0e68"
limit = 99000

url = f"{base_url}?resource_id={resource_id}&limit={limit}"
data = urlopen(url)
assert data.code == 200

response_dict = json.loads(data.read())
assert response_dict['success'] is True
result = response_dict['result']

pd.set_option('display.max_columns', None)
officials = pd.json_normalize(result["records"]) # full councillors list

# organize officals: filter & rearrange
officials = officials[~officials["Primary role"].isin(["None"])]
officials = officials.rename(columns={"Photo URL": "Photo", "District ID": "District #", "Address line 2": "Office", "Personal Website": "Personal website"})
officials["Full name"] = officials["First name"] + " " + officials["Last name"]
officials = officials[["Full name", "District #", "District name", "Primary role", "Email", "Website", "Phone", "Office", "Personal website", "Photo"]]

officials_list = []
website_list = []
for i in range(0, len(officials)):
    officials_list.append(officials.iloc[i,0])
    website_list.append(officials.iloc[i,5])

# committee data

csv_file = "static/data/committees.csv"
title_to_link = {}
committee_ids = []

with open(csv_file, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    committee_data = list(reader)
    for row in committee_data:
        title = row[0]
        id = row[1]
        title_to_link[title] = "/committees/" + id

def getCommittees(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    container = soup.find("div", {"id": "accordion-committees-boards"})

    if (container == None):
        return None

    links = container.find_all("p")

    results = []
    for p in links:
        a = p.find("a")

        if (a == None):
            continue

        title = a.get_text(strip=True)
        link = title_to_link.get(title, "")
        results.append([title, link])
    return results

committees_by_person = []

# get committees
for person in website_list:
    committees_by_person.append(getCommittees(person))

@app.route("/")
def home():
    full_name = session.get("my_official")
    motions_filtered = vr[vr["Full name"].isin([full_name])]
    motions_filtered = motions_filtered[["Agenda Item Title", "Vote", "Date & Time", "Result", "Agenda Item #", "Motion Type", "Vote Description"]]
    vote_highlight_data = load_data("in_the_news.json")
    motion_ids = set(vote_highlight_data.keys())
    motions_filtered = motions_filtered[motions_filtered["Agenda Item #"].isin(motion_ids)]
    if (full_name == None or full_name == "None"):
        this_id = 0
    else:
        this_id = officials_list.index(full_name)
    motions_dict = {
        row["Agenda Item #"]: [row["Vote"], row["Result"], row["Date & Time"]]
        for _, row in motions_filtered.iterrows()
    }

    return render_template("home.html", off_list=officials_list, news_dict=motions_dict, committee_items=committees_by_person[this_id])

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/motions-2022-2026")
def motions():
    return render_template("motions.html",
                            column_names=motions_all.columns.values,
                            row_data=list(motions_all.values.tolist()),
                            zip=zip,
                            name="")

## motions by official
@app.route("/councillors/<int:district_id>")
def motions_byName(district_id):
    if (-1 < district_id < len(officials)):
        full_name = officials_list[district_id]
        motions_filtered = vr[vr["Full name"].isin([full_name])]
        motions_filtered = motions_filtered[["Agenda Item Title", "Vote", "Date & Time", "Result", "Agenda Item #", "Motion Type", "Vote Description"]]
        return render_template("motions.html",
                                column_names=motions_filtered.columns.values,
                                row_data=list(motions_filtered.values.tolist()),
                                zip=zip,
                                name=full_name,
                                info=officials.iloc[district_id].tolist())
    else:
        return render_template("page_not_found.html"), 404
    
'''
@app.route('/official-highlights/default', methods=['GET'])
def get_official_highlights_default():
'''

@app.route('/official-highlights/<official_name>', methods=['GET'])
def get_official_highlights(official_name):
    if (official_name == "None"):
        return jsonify(load_data(f"official-highlights/None.json"))
    elif (official_name in officials_list):
        return jsonify(load_data(f"official-highlights/{official_name}.json"))
    else:
        return render_template("page_not_found.html"), 404

@app.route("/councillors")
def councillors():
    
    column_names=officials.columns.values
    row_data=list(officials.values.tolist())

    rows_as_dicts = [
        dict(zip(column_names, row))
        for row in row_data
    ]

    return render_template(
        "councillors.html",
        column_names=list(column_names),
        row_data=rows_as_dicts
    )

issues=["Housing", "Healthcare","Transportation", "Infrastructure"]
@app.route("/committees")
def committees():
    return render_template(
        "committees.html",
        data=committee_data,
        issues=issues
    )

## committees by official
@app.route("/committees/<id>")
def committee_byID(id):
    if (id in committee_ids):
        return render_template("motions.html",
                        column_names=motions_all.columns.values,
                        row_data=list(motions_all.values.tolist()),
                        zip=zip,
                        name="",
                        id=id,
                        id_list=committee_ids)
    else:
        return render_template("page_not_found.html"), 404


@app.route("/update-official", methods=["POST"])
def update_session():
    data = request.get_json()
    id = data.get("id")
    photo = data.get("photo")

    session["my_official"] = id
    session["my_photo"] = photo

    return jsonify({"status": "ok", "id": id})


@app.route('/nav')
def nav():
    return render_template("nav.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"), 404
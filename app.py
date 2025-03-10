from flask import Flask, url_for, jsonify, render_template
from markupsafe import escape
from urllib.request import urlopen
import json
import pandas as pd
from serpapi import GoogleSearch
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
DATA_FILE = "data.json"

## news articles

params = {
  "api_key": "3eccf5038307412e089db5ecfec9f4a35e6ed14b7b198e96a4e0b20ef4f0108f",
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

def load_data():
    try:
        return json.load(open(DATA_FILE, "r"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"message": "No data available"}

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(load_data())

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_api_data, "interval", days=1)
scheduler.start()

if __name__ == '__main__':
    fetch_api_data() # on startup
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
motions_all = vr[["Agenda Item Title", "Date & Time", "Result", "Agenda Item #", "Motion Type", "Vote Description"]].drop_duplicates()

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
for i in range(0, len(officials)):
    officials_list.append(officials.iloc[i,0])

@app.route("/")
def home():
    return render_template("home.html", off_list=officials_list)

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
@app.route("/motions-2022-2026/<int:district_id>")
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

@app.route("/councillors")
def councillors():
    return render_template("councillors.html",
                            column_names=officials.columns.values,
                            row_data=list(officials.values.tolist()),
                            zip=zip)

@app.route('/nav')
def nav():
    return app.send_static_file("nav.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"), 404
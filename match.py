from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
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
from urllib.request import urlopen
import urllib
import requests
import json
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'
}

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
# motions_all = vr[["Agenda Item Title", "Result", "Date & Time", "Agenda Item #", "Motion Type", "Vote Description"]].drop_duplicates()
motions_all = vr[["Agenda Item Title", "Agenda Item #"]].drop_duplicates()
motions_all = motions_all.head(200)

motions = motions_all.to_dict(orient="records")

with open("latest_city_council.json", "r", encoding='utf8') as f:
    articles = json.load(f)
articles = articles["articles"]



# get motion text
motion_text = []
for i in range(len(motions)):
    motion_query = motions[i]["Agenda Item #"]
    motion_query = urllib.parse.quote_plus(motion_query)
    url = "https://secure.toronto.ca/council/agenda-item.do?item=" + motion_query

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    allData = soup.find_all("div",{"class":"wep"})[0]

    text = []

    items = allData.find_all("p")
    for i in range(0,len(items)):
        text.append(items[i].text)

    motion_text.append(" ".join(text))
    text = []

model = SentenceTransformer('all-MiniLM-L6-v2')

print("Encoding motions...")

motion_texts = [motions[i]["Agenda Item Title"] + motion_text[i] for i in range(len(motions))]
motion_embeddings = model.encode(motion_texts, convert_to_numpy=True)

print("Encoding articles...")
article_texts = []
for a in articles:
    if a["motion_referenced"]:
        text = a["title"]
        if a.get("excerpt"):
            text += " " + a["excerpt"]
        if a.get("body"):
            text += " " + a["body"]
        article_texts.append(text)

article_embeddings = model.encode(article_texts, convert_to_numpy=True)

threshold = 0.55
matches = {}
for j, article in enumerate(articles):
    article_vec = article_embeddings[j]
    similarities = cosine_similarity([article_vec], motion_embeddings)[0]

    # get all motions above threshold
    matching_indices = np.where(similarities >= threshold)[0]

    if len(matching_indices) > 0:
        # sort by similarity score, descending
        sorted_indices = sorted(
            matching_indices,
            key=lambda idx: similarities[idx],
            reverse=True
        )

        # keep only top 2
        top_indices = sorted_indices[:2]

        matches[article["link"]] = [
            {
                "name": motions[idx]["Agenda Item Title"],
                "id": motions[idx]["Agenda Item #"],
                "score": float(similarities[idx])
            }
            for idx in top_indices
        ]
    else:
        matches[article["link"]] = None

# --- SAVE RESULTS ---
with open("motion_article_matches_bert_full.json", "w") as f:
    json.dump(matches, f, indent=2)

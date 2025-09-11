from collections import defaultdict
import json

DATA_FILE = "in_the_news_unformatted.json"

def load_data(file_name):
    try:
        return json.load(open(file_name, "r"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"message": "No data available"}

data = load_data(DATA_FILE)

motions = defaultdict(lambda: {"name": None, "articles": []})

for article_url, matches in data.items():
    if matches:
        for match in matches:
            motion_id = match["id"]
            motions[motion_id]["name"] = match["name"]
            motions[motion_id]["articles"].append(article_url)

motions = dict(motions)

output_file = "in_the_news.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(motions, f, indent=2, ensure_ascii=False)
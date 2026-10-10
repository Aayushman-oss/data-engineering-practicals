# Name: Ayushman Rajeev Verma
# extract_pipeline.py : REST API (JSON) + flat file (CSV) -> one clean report file
print("Name: Ayushman Rajeev Verma")
import json, time
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/todos?_limit=10"
CACHED_SAMPLE = [      # cached sample of the same API response, used only when the API is unreachable
    {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": False},
    {"userId": 1, "id": 2, "title": "quis ut nam facilis et officia qui", "completed": False},
    {"userId": 1, "id": 3, "title": "fugiat veniam minus", "completed": False},
    {"userId": 1, "id": 4, "title": "et porro tempora", "completed": True},
    {"userId": 1, "id": 5, "title": "laboriosam mollitia et enim quasi adipisci quia provident illum", "completed": False},
    {"userId": 1, "id": 6, "title": "qui ullam ratione quibusdam voluptatem quia omnis", "completed": False},
    {"userId": 1, "id": 7, "title": "illo expedita consequatur quia in", "completed": False},
    {"userId": 1, "id": 8, "title": "quo adipisci enim quam ut ab", "completed": True},
    {"userId": 1, "id": 9, "title": "molestiae perspiciatis ipsa", "completed": False},
    {"userId": 1, "id": 10, "title": "illo est ratione doloremque quia maiores aut", "completed": True},
]

def fetch_json(url, retries=3, wait=1):
    """GET with retries; returns (data, source_label)."""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=8)
            r.raise_for_status()
            return r.json(), "live API"
        except requests.RequestException as err:
            print(f"  attempt {attempt}/{retries} failed: {type(err).__name__}")
            time.sleep(wait)
    return CACHED_SAMPLE, "cached sample (API not reachable)"

def read_categories(path):
    pd.DataFrame({
        "id": range(1, 11),
        "category": ["work", "home", "work", "study", "home", "study", "work", "health", "home", "health"],
        "due_in_days": [2, 5, 1, 7, 3, 10, 2, 4, 6, 8],
    }).to_csv(path, index=False)            # create the flat file used in this lab
    return pd.read_csv(path)

def build_report(api_rows, cat_df):
    todos = pd.json_normalize(api_rows)
    todos["status"] = todos["completed"].map({True: "Done", False: "Pending"})
    todos["title_words"] = todos["title"].str.split().str.len()
    todos["title"] = todos["title"].str.capitalize()
    report = todos.merge(cat_df, on="id", how="left", validate="one_to_one")
    return report[["id", "userId", "title", "category", "due_in_days", "title_words", "status"]]

if __name__ == "__main__":
    print("Step 1: calling the API ...")
    rows, source = fetch_json(API_URL, retries=2, wait=0)
    print("Data source:", source, "| records:", len(rows))

    print("\nStep 2: reading the CSV file")
    categories = read_categories("task_categories.csv")
    print(categories.head(3).to_string(index=False))

    print("\nStep 3: merging and transforming")
    report = build_report(rows, categories)
    pd.set_option("display.width", 130, "display.max_colwidth", 38)
    print(report.to_string(index=False))

    print("\nStep 4: summary by category")
    print(report.groupby("category").agg(tasks=("id", "count"), avg_due_days=("due_in_days", "mean"),
                                         done=("status", lambda s: (s == "Done").sum())).round(1).to_string())
    report.to_csv("todo_report.csv", index=False)
    report.to_json("todo_report.json", orient="records", indent=1)
    print("\nSaved: todo_report.csv and todo_report.json")

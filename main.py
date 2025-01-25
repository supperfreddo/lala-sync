import requests
import time
import json
from pathlib import Path
from data_utils import *

API_URL = "https://www.lalachievements.com/api/user/char/"
CATEGORIES = get_categories()

with open(Path("config.json")) as config_file:
    config = json.load(config_file)

character_id = config["character_id"]
bearer_token = config["bearer_token"]


def main():
    if not Path(f"data/{character_id}").exists():
        create_local_files(character_id, CATEGORIES)

    for filename in get_import_files():
        category = filename.stem
        data = import_from_file(filename)
        if category in CATEGORIES:
            print(f"Processing {len(data)} entries for category {category}")
            # Entries are inside category variable
            update_via_api(
                category, get_pending_entries(category, preprocess_data(data))
            )
            print(f"Finished processing {category}\n")
        else:
            # Entries are inside a variable named as the category
            # TODO implement this
            print("Not implemented yet")

# Please do not increase the batch size above 50, as requested by the developer
# Also, ensure the sleep time remains reasonable to avoid stressing the server
def update_via_api(category, data, retries=3, batch_size=50, sleep_time=5):
    url = API_URL + str(character_id) + "/" + category + "/"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    for i in range(0, len(data), batch_size):
        batch = data[i : i + batch_size]
        ids = ",".join(str(e["id"]) for e in batch)
        response = requests.post(url + ids, headers=headers)
        if response.status_code == 200:
            for entry in batch:
                entry["added"] = True
            save_category(category, character_id, data)
            print(f"Successfully posted {len(batch)} entries to {category}")
        elif response.status_code == 401:
            print(
                "Incorrect JWT token, did you make sure to replace the bearer_token variable with your own?"
            )
            exit()
        else:
            print(f"Failed to post entries: {response.status_code} - {response.text}")
            if retries > 0:
                print(f"Retrying in {sleep_time} seconds")
                time.sleep(sleep_time)
                update_via_api(category, batch, retries - 1)
            else:
                print("No more retries left")
        time.sleep(sleep_time)


def get_pending_entries(category, data):
    pending_entries = []
    entries = load_category(category, character_id)
    pending = [e for e in entries if not e["added"]]

    pending_entries_dict = {e["id"]: e for e in pending if e["id"] is not None}
    pending_entries_name_dict = {e["name"]: e for e in pending if e["name"] is not None}

    already_added_count = 0

    for entry in data:
        pending_entry = None
        if entry["id"] is not None and entry["name"] is not None:
            pending_entry_by_id = pending_entries_dict.get(entry["id"])
            pending_entry_by_name = pending_entries_name_dict.get(entry["name"])
            if (
                pending_entry_by_id == pending_entry_by_name
                and pending_entry_by_id is not None
            ):
                pending_entry = pending_entry_by_id
        elif entry["id"] is not None:
            pending_entry = pending_entries_dict.get(entry["id"])
        elif entry["name"] is not None:
            pending_entry = pending_entries_name_dict.get(entry["name"])

        if pending_entry is not None:
            if pending_entry not in pending_entries:
                pending_entries.append(pending_entry)

    already_added_count = len(entries) - len(pending)

    print(f"Entries to add: {len(pending_entries)}")
    print(f"Entries already added: {already_added_count}")
    # BUG duplicate entries are counted as not found
    print(
        f"Entries not found: {len(data) - len(pending_entries) - already_added_count}"
    )

    return pending_entries


if __name__ == "__main__":
    main()

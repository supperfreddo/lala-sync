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
            # Entries are inside category variable
            update_via_api(
                category, get_pending_entries(category, preprocess_data(data))
            )
        else:
            # Entries are inside a variable named as the category
            # TODO implement this
            print(f"Category '{category}' not found. Mass import file not supported yet.")


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
    discard_entries = []
    entries = load_category(category, character_id)

    entries_dict = {e["id"]: e for e in entries if e["id"] is not None}
    entries_name_dict = {e["name"].lower(): e for e in entries if e["name"] is not None}

    for entry in data:
        pending_entry = None
        if entry["id"] is not None and entry["name"] is not None:
            entry_by_id = entries_dict.get(entry["id"])
            entry_by_name = entries_name_dict.get(entry["name"].lower())
            if entry_by_id == entry_by_name and entry_by_id is not None:
                pending_entry = entry_by_id
        elif entry["id"] is not None:
            pending_entry = entries_dict.get(entry["id"])
        elif entry["name"] is not None:
            pending_entry = entries_name_dict.get(entry["name"].lower())

        if pending_entry is not None:
            if pending_entry not in pending_entries and not pending_entry["added"]:
                pending_entries.append(pending_entry)
        else:
            if entry not in discard_entries:
                discard_entries.append(entry)

    if discard_entries:
        print(f"{len(discard_entries)} entries not found for category {category}")
        show_not_found = input(
            "Do you want to see the entries that are not found? (yes/no): "
        )

        if show_not_found.lower() == "yes" or show_not_found.lower() == "y":
            for entry in discard_entries:
                print(entry)
            input("Press any key to continue...")

    return pending_entries


if __name__ == "__main__":
    main()

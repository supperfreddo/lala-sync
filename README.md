# Lala sync
Lala Sync is a simple web automation script designed to sync data with [Lala achievements](https://www.lalachievements.com/).

## Configuration
The configuration file [config.json](config.json) contains settings required for the synchronization process. To get your `character_id`, navigate to your character's page on the Lala Achievements website and copy the ID from the URL. To get your `bearer_token`, inspect the network calls while adding or removing an entry on the website. Look for the `POST` or `DELETE` request and copy the `bearer_token` from the request headers.

## Usage
To set up the import files, create a JSON file in the imports directory. Each file should contain an array of objects with either an id, name, or both, representing the entries that need to be added. The name of the JSON file should correspond to the category name (e.g., fashions.json for fashion entries).

Run the main script to start the synchronization process: `python main.py`

## API Usage Guidelines
To avoid spamming the API, please adhere to the following guidelines:
- Do not increase the batch size above 50 entries per call.
- Ensure there is a reasonable delay between consecutive API calls to avoid stressing the server.

The script is configured to handle these guidelines by default, but please be mindful of them if you make any modifications.
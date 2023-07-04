import csv
import json
import os
from arango import ArangoClient
from libretranslatepy import LibreTranslateAPI

# read csv file
directory = './CSV_Input/'
csv_file = max([os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')], key=os.path.getctime)

# Connect to ArangoDB
client = ArangoClient(hosts="http://127.0.0.1:8529")
db = client.db('academicontology')

# Parse the CSV data and put into data list

data = []
with open(csv_file, 'r', newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Extract the labels and text from the columns
        labels_text = row['label']
        annotations = json.loads(labels_text)
        for annotation in annotations:
            extracted_text = annotation['text']
            extracted_labels = annotation['labels']
            entry = {
                'text': extracted_text,
                'labels': extracted_labels
            }
            data.append(entry)

# translate the data list
lt = LibreTranslateAPI("https://translate.argosopentech.com/")
not_translate_label = [['Person'], ['Personel'], ['Student'], ['Employee'], ['Lecturer'], ['Professor'], ['Guest Student'], ['Regular Student'], ['Campus']]

translated_data = []

for entry in data:
    if entry['labels'] not in not_translate_label:
        text = entry['text']
        origin_language_dict = lt.detect(text)
        origin_language = origin_language_dict[0]['language']

        text = lt.translate(text, origin_language, 'de')

        translated_entry = {'text': text, 'labels': entry['labels']}
        print(translated_entry)

        translated_data.append(translated_entry)

    else:
        translated_data.append(entry)
        print(entry)

# Create nodes in ArangoDB
for entry in translated_data:
    collection_name = entry['labels'][0]  # Assumes only one label per entry
    text = entry['text']

    # Check if the collection exists, create it if not
    if not db.has_collection(collection_name):
        db.create_collection(collection_name)

    # Insert the node document into the collection
    collection = db.collection(collection_name)
    collection.insert({'name': text})

    print(f"Inserted node: {collection_name} - {text}")


# write translated data into new json file output.json
# with open('output.json', 'w') as outfile:
    #json.dump(translated_data, outfile)


from libretranslatepy import LibreTranslateAPI
import csv
import os
import json

# read csv file
directory = './CSV_Input/'
csv_file = max([os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')], key=os.path.getctime)

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
translate_label = [['Project'], ['Faculty']]

translated_data = []

for entry in data:
    if entry['labels'] in translate_label:
        text = entry['text']
        origin_language_dict = lt.detect(text)
        origin_language = origin_language_dict[0]['language']

        text = lt.translate(text, origin_language, 'en')

        translated_entry = {'text': text, 'labels': entry['labels']}
        print(translated_entry)

        translated_data.append(translated_entry)

    else:
        translated_data.append(entry)
        print(entry)


# write translated data into new json file output.json
with open('output.json', 'w') as outfile:
    json.dump(translated_data, outfile)
    
print("done")

# SALT - Digilogue Data Visualisation Project
# September 2020
## Author: Ceren Kocaoğullar
## Description: This program prepares two categories of data for our project: 
##              SALT Tagging based (T) and Search/Knowlege API based Connection (G)

##############################################################################

import wptools
import re
import csv
import os
import json
import random
import xml.etree.ElementTree as ET

def main():
    for foldername in os.listdir('data/'):
        search_and_write_results(foldername, 'data/' + foldername)
        
def search_and_write_results(foldername, path):
    if '.' not in foldername:
        if foldername.isnumeric():
            data_id = get_and_write_metadata(path)
            categories = cumulative_search(data_id)
            write_search_results(data_id, categories)
        else:
            for foldername in os.listdir(path):
                search_and_write_results(foldername, path + '/' + foldername)


# Uses SALT-provided xml files to collect useful metadata
def get_and_write_metadata(path):
    temp_data = dict()
    tree = ET.parse(f'{path}/dublin_core.xml')
    root = tree.getroot()
    with open('data.json', 'r+', encoding='utf-8') as f:
        if len(f.readlines()) != 0:
            f.seek(0)
            data = json.load(f)
        else:
            data = dict()
        for child in root:
            if child.attrib['qualifier'] == 'uri':
                data_id = child.text.split('/')[-1]
                data[data_id] = dict()
            if child.attrib['qualifier'] == 'spatial':
                temp_data['spatial'] = child.text
            if child.attrib['element'] == 'title':
                temp_data['title'] = child.text
            if child.attrib['element'] == 'subject':
                temp_data['subject'] = temp_data['subject'] + child.text + ", " if 'subject' in temp_data else child.text + ", "
            if child.attrib['element'] == 'date' and child.attrib['qualifier'] == 'issued':
                temp_data['date_issued'] = child.text
            if child.attrib['element'] == 'format' and child.attrib['qualifier'] == 'none':
                temp_data['format'] = temp_data['format'] + child.text + ", " if 'format' in temp_data else child.text + ", "
            if child.attrib['element'] == 'type' and child.attrib['qualifier'] == 'none':
                temp_data['type'] = child.text
            if child.attrib['element'] == 'creator' and child.attrib['qualifier'] == 'none':
                temp_data['creator'] = child.text
            if child.attrib['element'] == 'description' and child.attrib['qualifier'] == 'none':
                temp_data['description'] = child.text
        data[data_id]['salt_metadata'] = temp_data
        f.seek(0)        
        json.dump(data, f, ensure_ascii=False, indent=4)
        temp_data.clear()
        f.truncate() 
    return data_id   

# Seeks SALT-provided title metadata to detect proper nouns (i.e. the words/word groups that start with capital letters)
# Ignores the first word unless it's followed by another proper noun since every sentence starts with a capital letter 
def find_search_keywords(data_id):
    keywords = []
    with open('data.json', 'r') as f:
        f.seek(0)
        data = json.load(f)
        words = [x.strip() for x in data[data_id]['salt_metadata']['title'].replace(',', '').split('-')[0].split()]
        #words = [x.strip() for x in "Nesrin Bağana, Müzdan Arel, Hakkı Said Tez ve muhtemelen Fatma Semiramis Kocainan ile Güzin Kocabaş'ın çektirdikleri boy fotoğrafı".split('-')[0].split()]
        keyword = ''
        for i in range(len(words)):
            if "," in words[i]:
                words[i] = words[i].split("'")[0]
            if "'" in words[i]:
                words[i] = words[i].split("'")[0]
            if "’" in words[i]:
                words[i] = words[i].split("’")[0]
            if words[i][0].isupper():
                if keyword:
                    keyword = keyword + ' '
                keyword += words[i]
                if "," in words[i]:
                    words[i] = words[i].replace(",", "")
                    if keyword and keyword not in keywords:
                        keywords.append(keyword)
                    keyword = ''
            elif words[i][0] == "(":
                pass
            else:
                if (keyword and i >= 1) and keyword not in keywords:
                    keywords.append(keyword)
                keyword = ''
        if 'subject' in data[data_id]['salt_metadata'].keys():
            keywords += [x.strip() for x in data[data_id]['salt_metadata']['subject'].split(',')]
        while '' in keywords: keywords.remove('')
        print(f'hello {keywords}')
        return keywords

# Performs a search using a Wikidata API and returns the results
def cumulative_search(data_id):
    categories = dict()
    keywords = find_search_keywords(data_id)
    for keyword in keywords:
        try:
            page = wptools.page(keyword, lang='tr')
            data = page.get_parse().data
            categories[keyword] = get_wikipedia_categories(data)
        except:
            print("Could not execute search")
    return categories
    
# Returns the categories in the Wikipedia page of the searched item
def get_wikipedia_categories(data):
    wikitext = data['wikitext']
    pattern = r'^\[\[Kategori:.*\]\]$'
    matches = re.finditer(pattern, wikitext, re.MULTILINE)
    categories = []
    for matchNum, match in enumerate(matches, start=1): 
        categories.append(re.sub(r'\[|Kategori|:|\]', '', match.group()))
    return categories

# Stores search results in a json file
def write_search_results(data_id, categories):
    with open('data.json', 'r+') as f:
        if len(f.readlines()) != 0:
                f.seek(0)
                data = json.load(f)
        else:
            data = dict()
        if categories:
            data[data_id]['search_res'] = categories
        f.seek(0)        
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.truncate()
    

if __name__ == "__main__":
    main()
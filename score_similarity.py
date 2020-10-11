# SALT - Digilogue Data Visualisation Project
# September 2020
## Author: Ceren Kocaoğullar
## Description: This program scores similarity scores based on this documentation: 
#               https://www.notion.so/Similarity-Scoring-62a412f4b5aa4aa4b9d4368a6e90456d (prepared by Genco Levi)

##############################################################################

import json
import random
import re

# Coefficients of each similarity category as documented 
a_G = 1
a_V = 1
a_C = 1
a_T = 1
a_U = 1

def main():
    with open('data.json','r') as f:
        data = json.load(f)
        f.close()
    data_ids = data.keys()

    with open('similarity_scores.json', 'r+') as f:
        if len(f.readlines()) != 0:
            f.seek(0)
            similarity_data = json.load(f)
        else:
            similarity_data = dict()
        for data_id1 in data_ids:
            top_100_search = {-1: (-1, ())}
            min_search_score = (-1, -1)
            top_100_salt_metadata = {-1: (-1, ())}
            min_salt_metadata_score = (-1, -1)
            for data_id2 in data_ids:
                if not data_id1 == data_id2:
                    if data_id1 not in similarity_data.keys():
                        similarity_data[data_id1] = dict()
                    # if data_id2 not in similarity_data[data_id1].keys():
                    #     similarity_data[data_id1][data_id2] = dict()
                    search_score, search_intersection = score_results('search_res', data_id1, data_id2, data)
                    salt_metadata_score, salt_metadata_intersection = score_results('salt_metadata', data_id1, data_id2, data)
                    min_search_score = adjust_top_100_score(data_id2, top_100_search, search_intersection, search_score, min_search_score)
                    min_salt_metadata_score = adjust_top_100_score(data_id2, top_100_salt_metadata, salt_metadata_intersection, salt_metadata_score, min_salt_metadata_score)
            similarity_data[data_id1]['search_res'] = top_100_search
            similarity_data[data_id1]['salt_metadata'] = top_100_salt_metadata
            print(similarity_data[data_id1])
        ## OVERALL SCORING
        # for data_id1 in data_ids:
        #     for data_id2 in data_ids:
        #         if not data_id1 == data_id2:
        #             similarity_data[data_id1][data_id2]['overall'] = score_overall(data_id1, data_id2, similarity_data) 
        
        json.dump(similarity_data, f, ensure_ascii=False, indent=4)
        f.truncate()

def adjust_top_100_score(data_id, top_100_scores, search_intersection, score, min_score):
    if len(top_100_scores) < 100:
            top_100_scores[data_id] = (score, search_intersection)
    elif score > min_score[1]:
            del top_100_scores[min_score[0]]
            top_100_scores[data_id] = (score, search_intersection)
    min_s = min([x[0] for x in top_100_scores.values()])
    min_score = (get_key(top_100_scores, min_s), min_s)
    return min_score

# Calculates overall Similarity Score for a given pair (S)
def score_overall(data_id1, data_id2, data):
    G = data[data_id1][data_id2]['search_res']
    V = data[data_id1][data_id2]['vis_similarity']
    C = data[data_id1][data_id2]['object_match']
    T = data[data_id1][data_id2]['salt_metadata']
    U = data[data_id1][data_id2]['user_connection']
    return a_G * G + a_V * V + a_C * C + a_T * T + a_U * U

# Calculates Search/Knowlege API based Connection (G) or Calculates SALT Tagging based (T) similarity score by taking the 
# common words occuring in the search results of a couple of items
def score_results(res_type, data_id1, data_id2, data):
    search_res1 = set(prepare_word_comparison(res_type, data_id1, data))
    search_res2 = set(prepare_word_comparison(res_type, data_id2, data))
    total_words = len(search_res1) + len(search_res2)
    intersection = get_word_intersection(search_res1, search_res2)
    return 0 if total_words == 0 else len(intersection) / total_words, intersection

def get_word_intersection(res1, res2):
    intersection = list()
    for item1 in res1:
        for item2 in res2:
            if item1 in item2:
                intersection.append(item1)
                if item1 != item2:
                    intersection.append(item2)
    return intersection

# Splits sentences into words to prepare them for Search/Knowlege API based Connection (G) / SALT Tagging 
# based (T) comparison
def prepare_word_comparison(tag, data_id, data):
    prepared = []
    if tag in data[data_id].keys():
        for key in data[data_id][tag]:
            if isinstance(data[data_id][tag][key], list):
                for item in data[data_id][tag][key]:
                    #item = item.replace('|', '').replace(',', '').split('-').strip()
                    for i in re.split(',|-', item):
                        i = i.replace('\|', '').replace(',', '').strip()
                        if i not in prepared and item != '':
                            prepared.append(item)
            elif key != 'title' and key!= 'description':
                items = [x.replace('\|', '').replace(',', '').strip() for x in re.split(',|-|:', data[data_id][tag][key])]
                for item in items:
                    if item not in prepared and item != '':
                        if key == 'format' and item[0].isnumeric():
                            pass
                        else:
                            prepared.append(item)
    return prepared

def prepare_salt_metadata_word_comparison(tag, data_id, data):
    prepared = []
    if tag in data[data_id].keys():
        for key in data[data_id][tag]:
            if type(data[data_id][tag][key]) == list:
                for item in data[data_id][tag][key]:
                    prepared += [x.strip().lower() for x in item.split()]
            else:
                prepared += [x.strip().lower() for x in data[data_id][tag][key].split()]   
    return prepared

def get_key(my_dict, val): 
    for key, value in my_dict.items(): 
         if val == value[0]: 
             return key 
  
    return "key doesn't exist"

#############
## GENERATES MOCK DATA, NOT USING ANYMORE!!!
# # Generates mock similarity data for Visual Similarity (V), Image captioning/object recognition (C) and 
# # User Made Connection (U) categories.
# def generate_mock_scores(data_id1, data_id2):
#     # Randomly assigns a float between 1-0 to the visual similarity score
#     vis_similarity = random.random()
#     # Randomly assigns 1 or 0 to the visual similarity score
#     object_match = random.choice([0, 1])
#     # Randomly assigns an int between 0-10 to the user connection score
#     user_connection = random.randint(0, 10)
#     return vis_similarity, object_match, user_connection

if __name__ == "__main__":
    main()
# SALT - Digilogue Data Visualisation Project
# September 2020
## Author: Ceren Kocaoğullar
## Description: This program scores similarity scores based on this documentation: 
#               https://www.notion.so/Similarity-Scoring-62a412f4b5aa4aa4b9d4368a6e90456d (prepared by Genco Levi)

##############################################################################

import json
import random

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
            for data_id2 in data_ids:
                if not data_id1 == data_id2:
                    if data_id1 not in similarity_data.keys():
                        similarity_data[data_id1] = dict()
                    if data_id2 not in similarity_data[data_id1].keys():
                        similarity_data[data_id1][data_id2] = dict()
                    vis_similarity, object_match, user_connection = generate_mock_scores(data_id1, data_id2)
                    similarity_data[data_id1][data_id2]['vis_similarity'] = vis_similarity
                    similarity_data[data_id1][data_id2]['object_match'] = object_match
                    similarity_data[data_id1][data_id2]['user_connection'] = user_connection
                    similarity_data[data_id1][data_id2]['search_res'] = score_search_res(data_id1, data_id2, data)
                    similarity_data[data_id1][data_id2]['salt_metadata'] = score_salt_metadata(data_id1, data_id2, data)
        # Overall scoring
        for data_id1 in data_ids:
            for data_id2 in data_ids:
                if not data_id1 == data_id2:
                    similarity_data[data_id1][data_id2]['overall'] = score_overall(data_id1, data_id2, similarity_data) 
        json.dump(similarity_data, f, ensure_ascii=False, indent=4)
        f.truncate()

# Calculates overall Similarity Score for a given pair (S)
def score_overall(data_id1, data_id2, data):
    G = data[data_id1][data_id2]['search_res']
    V = data[data_id1][data_id2]['vis_similarity']
    C = data[data_id1][data_id2]['object_match']
    T = data[data_id1][data_id2]['salt_metadata']
    U = data[data_id1][data_id2]['user_connection']
    return a_G * G + a_V * V + a_C * C + a_T * T + a_U * U

# Calculates Search/Knowlege API based Connection (G) similarity score by taking the 
# common words occuring in the search results of a couple of items
def score_search_res(data_id1, data_id2, data):
    search_res1 = set(prepare_word_comparison('search_res', data_id1, data))
    search_res2 = set(prepare_word_comparison('search_res', data_id2, data))
    total_words = len(search_res1) + len(search_res2)
    return 0 if total_words == 0 else len(search_res1.intersection(search_res2)) / total_words

# Calculates SALT Tagging based (T) similarity score by taking the 
# common words occuring in the search results of a couple of items
def score_salt_metadata(data_id1, data_id2, data):
    salt_metadata1 = set(prepare_word_comparison('salt_metadata', data_id1, data))
    salt_metadata2 = set(prepare_word_comparison('salt_metadata', data_id2, data))
    total_words = len(salt_metadata1) + len(salt_metadata2)
    return 0 if total_words == 0 else len(salt_metadata1.intersection(salt_metadata2)) / total_words

# Splits sentences into words to prepare them for Search/Knowlege API based Connection (G) / SALT Tagging 
# based (T) comparison
def prepare_word_comparison(tag, data_id, data):
    prepared = []
    if tag in data[data_id].keys():
        for key in data[data_id][tag]:
            if type(data[data_id][tag][key]) == list:
                print("yes list")
                for item in data[data_id][tag][key]:
                    prepared += [x.strip().lower() for x in item.split()]
            else:
                prepared += [x.strip().lower() for x in data[data_id][tag][key].split()]   
    return prepared

# Generates mock similarity data for Visual Similarity (V), Image captioning/object recognition (C) and 
# User Made Connection (U) categories.
def generate_mock_scores(data_id1, data_id2):
    # Randomly assigns a float between 1-0 to the visual similarity score
    vis_similarity = random.random()
    # Randomly assigns 1 or 0 to the visual similarity score
    object_match = random.choice([0, 1])
    # Randomly assigns an int between 0-10 to the user connection score
    user_connection = random.randint(0, 10)
    return vis_similarity, object_match, user_connection

if __name__ == "__main__":
    main()
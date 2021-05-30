from os import getcwd
import requests
from os import path, getcwd
import json
filepath = getcwd()


def in_local(word):
    word = word.replace(' ', '-').lower()
    file = path.join(filepath, 'synonyms', f'{word}.json')
    if path.isfile(file) is True:
        with open(file, 'r') as f:
            return json.load(f), True
    return {}, False


def save_to_local(word, dict_):
    file = path.join(filepath, 'synonyms', f'{word}.json')
    with open(file, 'w+') as f:
        json.dump(dict_, f)


def synonym(word):
    resp = ""
    if (resp := in_local(word))[1] == True:
        resp = resp[0]
    else:
        resp = requests.get(
            f'https://tuna.thesaurus.com/pageData/'
            f'{word.replace(" ", "-").lower()}').json()['data']
        if resp is None:
            return []
        else:
            save_to_local(word, resp)
    return [synonym['term'] for defn in resp['definitionData']['definitions'] for synonym in defn['synonyms']]

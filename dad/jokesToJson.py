#!/usr/bin/python

import json
from pprint import pprint

def main():
    data = None
    with open('config.json') as json_file, open('dadJokes.txt') as text_file:
        data = json.load(json_file)
        for line in text_file:
            data['speak']['dadName']['responses']['joke'].append([line.split('~')[0], line.split('~')[1]])

    with open('config_test.json', 'w') as json_file:
        json_file.write(str(data))

if __name__ == "__main__":
    main()
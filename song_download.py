import sys
import json
import os.path
import urllib.request as req

def main():
    if len(sys.argv) != 2:
        print('specify a file')

    # clear out files in songs except temp.txt

    # load file
    input_file = open(sys.argv[1], 'r',encoding='utf-8')
    raw_json_str = input_file.read().strip()
    data = json.loads(raw_json_str)
    for entry in data:
        print('Downloading',entry['url'])
        if os.path.isfile('songs/' + entry['url'].split('/')[-1]):
            print('Found file, skipping...')
            continue
        try:
            req.urlretrieve(entry['url'], 'songs/' + entry['url'].split('/')[-1])
        except:
            print('Could not download file:',entry['url'])


if __name__ == "__main__":
    print('hey hey hey start dash!')
    main()
    

import sys
import json
import urllib.request as req

def main():
    if len(sys.argv) != 2:
        print('specify a file')

    # clear out files in songs except temp.txt

    # load file
    input_file = open(sys.argv[1])
    raw_json_str = input_file.read()
    data = json.loads(raw_json_str)
    for entry in data:
        print('Downloading',entry['url'])
        req.urlretrieve(entry['url'], 'songs/' + entry['url'].split('/')[-1])


if __name__ == "__main__":
    print('hey hey hey start dash!')
    main()
    

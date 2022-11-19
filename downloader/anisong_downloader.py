import json, os, sys

def add_numbers_to_inserts(json_data):
    # initialize counter to 1
    insert_counter = 1
    for song_json in json_data:
        if 'Insert' in song_json['songType']:
            song_json['songType'] = 'Insert Song ' + str(insert_counter)
            insert_counter += 1
    return json_data

def download_song(songdict, output_dir):
    pass

def fix_metadata(songdict, output_file):
    pass

if __name__ == '__main__':
    print('Hey Hey Hey start dash')
    if len(sys.argv) == 1:
        print('Downloads songs from a certain animesong database.')
        print('Usage: anisong_downloader <path to json> <output path>')
        sys.exit(0)
    elif len(sys.argv) == 2:
        # json file is provided, assume that the 
        # download location is pwd.
        json_filename = sys.argv[1]
        download_dir = os.getcwd()
    elif len(sys.argv) >=3:
        json_filename = sys.argv[1]
        download_dir = sys.argv[2]
    
    # load file
    file = open(json_filename, encoding='utf-8')
    json_data = json.load(file, encoding='utf-8')
    file.close()

    # add numberings to inserts
    json_data = add_numbers_to_inserts(json_data)

    # download the files
    for song_json in 

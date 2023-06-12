import json, os, sys, re
import urllib.request as req
import eyed3

def add_numbers_to_inserts(json_data):
    # initialize counter to 1
    insert_counter = 1
    for song_json in json_data:
        if 'Insert' in song_json['songType']:
            song_json['songType'] = 'Insert Song ' + str(insert_counter)
            insert_counter += 1
    return json_data


def get_songtype(song_json):
    if 'Opening' in song_json['songType']:
        songtype = song_json['songType'].replace('Opening ','OP')
    elif 'Ending' in song_json['songType']:
        songtype = song_json['songType'].replace('Ending ','ED')
    elif 'Insert' in song_json['songType']:
        songtype = song_json['songType'].replace('Insert Song ','IN')
    return songtype


def download_song(song_json, output_dir):
    songtype = get_songtype(song_json)
    output_filename = ''.join(x for x in song_json['animeENName'] if x.isalnum()) + '_' + songtype + '_' + str(song_json['annSongId']) + '.mp3'
    print('Downloading {0}'.format(output_filename))

    # set up the filename (important!).
    full_output_path = os.path.join(output_dir,output_filename)

    try:
        req.urlretrieve(song_json['audio'], full_output_path)
    except:
        print('Failed to download {0}'.format(song_json['audio']))

    return full_output_path


def fix_metadata(song_json, output_file):
    print('Fixing metadata for {0}'.format(os.path.basename(output_file)))

    songtype = get_songtype(song_json)
    songtype = songtype[0:2] + ' ' + songtype[2:]

    audiofile = eyed3.load(output_file)
    if audiofile.tag is None:
        audiofile.initTag()

    anime_name = song_json['animeENName'] if len(song_json['animeENName']) < len(song_json['animeJPName']) else song_json['animeJPName']

    audiofile.tag.title = anime_name + ' ' + songtype + ' - ' +song_json['songName']
    audiofile.tag.track_num = re.findall('\d+',song_json['songType'])[-1]
    audiofile.tag.artist = ';'.join([artist['names'][0] for artist in song_json['artists']])

    audiofile.tag.save()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Downloads songs from a certain animesong database.')
        print('Usage: anisong_downloader.py <output path>  <path to json> ...')
        sys.exit(0)
    elif len(sys.argv) >=3:
        json_filenames = sys.argv[2:]
        download_dir = sys.argv[1]

    for json_filename in json_filenames:
        # load file
        file = open(json_filename, encoding='utf-8')
        json_data = json.load(file, encoding='utf-8')
        file.close()

        # add numberings to inserts
        json_data = add_numbers_to_inserts(json_data)

        # download the files
        for song_json in json_data:
            output_filename = download_song(song_json, download_dir)
            fix_metadata(song_json, output_filename)
    
    print('Done!')

import json
from Utils import get_filenames_in_order
import getopt
import sys
from datetime import datetime, timedelta
import pandas as pd

def parse_file(filename, date, username, annid, cum_song_data):
    # load file
    file = open(filename, encoding='utf-8')
    json_data = json.load(file, encoding='utf-8')
    file.close()
    print('\tLoading data for',filename)
    
    # iterate through each song, assuming that later songs came later in time
    # cum_song_data = {}
    show_data = {'name' : '', 'annid' : annid}
    for song_data in json_data:
        if song_data['annId'] == annid:
            # save off key for saving data
            song_key = (song_data['name'], song_data['artist'])
            max_res = str(max([int(num) for num in song_data['urls']['catbox'].keys()]))
            show_data['name'] = song_data['anime']['romaji']

            if song_key not in cum_song_data:
                cum_song_data[song_key] = {'Song name' : song_data['name'],
                                            'Artist' : song_data['artist'],
                                            'Song type' : song_data['type'],
                                            'Correct streak' : 0,
                                            'Number times correct' : 0,
                                            'Number times wrong' : 0,
                                            'Number of times seen' : 0,
                                            'Date last time correct' : None,
                                            'Date last time wrong' : None,
                                            'webm url' : song_data['urls']['catbox'][max_res]}

            # get specific player data
            player_data = [player_data for player_data in song_data['players'] if player_data['name'].lower() == username.lower()]
            if(len(player_data) == 0): continue
            player_data = player_data[0]

            # populate with information
            if song_data['correct']:
                cum_song_data[song_key]['Number times correct'] += 1
                cum_song_data[song_key]['Date last time correct'] = date
                cum_song_data[song_key]['Correct streak'] = 1 if cum_song_data[song_key]['Correct streak'] <= 0 \
                                                                    else cum_song_data[song_key]['Correct streak'] + 1
            else:
                cum_song_data[song_key]['Number times wrong'] += 1
                cum_song_data[song_key]['Date last time wrong'] = date
                cum_song_data[song_key]['Correct streak'] = -1 if cum_song_data[song_key]['Correct streak'] >= 0 \
                                                                    else cum_song_data[song_key]['Correct streak'] - 1
            cum_song_data[song_key]['Number of times seen'] += 1
    return cum_song_data, show_data

def make_report(filenames, username, annid):
    cum_song_data = {}
    for date, filename in filenames:
        cum_song_data, show_data = parse_file(filename, date, username, annid, cum_song_data)
    # convert to df
    pd_data = {
        'Song name' : [name for name, _ in cum_song_data],
        'Artist' : [artist for _, artist in cum_song_data],
        'Song type' : [cum_song_data[key]['Song type'] for key in cum_song_data],
        'Correct streak' : [cum_song_data[key]['Correct streak'] for key in cum_song_data],
        'Number times correct' : [cum_song_data[key]['Number times correct'] for key in cum_song_data],
        'Number times wrong' : [cum_song_data[key]['Number times wrong'] for key in cum_song_data],
        'Number of times seen' : [cum_song_data[key]['Number of times seen'] for key in cum_song_data],
        'Date last time correct' : [cum_song_data[key]['Date last time correct'] for key in cum_song_data],
        'Date last time wrong' : [cum_song_data[key]['Date last time wrong'] for key in cum_song_data],
        'webm url' : [cum_song_data[key]['webm url'] for key in cum_song_data]
    }
    df = pd.DataFrame(data=pd_data)
    df = df.set_index(['Song name', 'Artist', 'Song type'])
    df.to_excel('output-' + str(annid) + '-' + show_data['name'] + '.xlsx')
    return df, show_data


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], '', ['username=', 'min-date=', 'data=', 'annid='])
    username = ''
    annid = -1
    min_date = (datetime.today() - timedelta(weeks=7)).strftime('%Y-%m-%d')
    datadir = '../amq/data/general'
    for o, a in opts:
        if o == '--username':
            username = a
        elif o == '--min-date':
            min_date = a
        elif o == '--data':
            datadir = a
        elif o == '--annid':
            annid = int(a)
    if username == '':
        print('Missing username!', file=sys.stderr)
        sys.exit(1) 
    elif annid <= 0:
        print('Missing annid to search on!', file=sys.stderr)
        sys.exit(1)
    print('Looking at data for', username,'for show with annid:',str(annid))

    all_filenames = get_filenames_in_order(datadir)
    df, show_data = make_report(all_filenames, username, annid)
    print(df[['Correct streak', 'Number of times seen', 'webm url']])
    print()
    print(show_data)

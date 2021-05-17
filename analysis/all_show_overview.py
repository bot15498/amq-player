import getopt
import json
import os
import pandas as pd
import sys
from datetime import datetime, timedelta

def load_data_in_dir(min_date:str, username:str, datadir: str='../amq/data/general'):
    # walk data directory for any json file
    all_files_raw = os.walk(datadir)
    all_files = []
    for path, _, filenames in all_files_raw:
        for filename in filenames:
            if filename.split('.')[-1].lower() == 'json':
                all_files.append(path + '/' + filename)

    agg_data = {}
    # probably should multithread this at some point
    for filename in all_files:
        file = open(filename, encoding='utf-8')
        json_data = json.load(file, encoding='utf-8')
        file_datetime = datetime.fromtimestamp(os.path.getmtime(filename))
        file.close()
        print('\tLoading data for',filename)
        for song_data in json_data:
            # add show if it doesn't exist yet
            if song_data['annId'] not in agg_data:
                curr_annid = song_data['annId']
                agg_data[curr_annid] = {'show name': song_data['anime']['romaji'],
                                                'in list?' : True,
                                                'date last correct' : '', 'date last wrong': '',
                                                'number correct' : 0, 
                                                'number wrong' : 0,
                                                'total number seen' : 0,
                                                'song of last correct' : '', 'url of last correct' : '',
                                                'song of last wrong' : '', 'url of last wrong' : ''}

            # get specific player data
            player_data = [player_data for player_data in song_data['players'] if player_data['name'].lower() == username.lower()]
            if(len(player_data) == 0): continue
            player_data = player_data[0]

            # get from list data
            list_check_count = len([True for list_data in song_data['fromList'] if list_data['name'].lower() == username.lower()])
            list_check = True if list_check_count == 1 else False
            agg_data[curr_annid]['inList'] = list_check

            # get correct or not and populate
            agg_data[curr_annid]['total number seen'] += 1
            if player_data['correct']:
                agg_data[curr_annid]['number correct'] += 1
                if agg_data[curr_annid]['date last correct'] == '' or agg_data[curr_annid]['date last correct'] < file_datetime:
                    agg_data[curr_annid]['date last correct'] = file_datetime
                    agg_data[curr_annid]['song of last correct'] = song_data['name'] + ' - ' + song_data['artist']
                    max_res = str(max([int(num) for num in song_data['urls']['catbox'].keys()]))
                    agg_data[curr_annid]['url of last correct'] = song_data['urls']['catbox'][max_res]
            else:
                agg_data[curr_annid]['number wrong'] += 1
                if agg_data[curr_annid]['date last wrong'] == '' or agg_data[curr_annid]['date last wrong'] < file_datetime:
                    agg_data[curr_annid]['date last wrong'] = file_datetime
                    agg_data[curr_annid]['song of last wrong'] = song_data['name'] + ' - ' + song_data['artist']
                    max_res = str(max([int(num) for num in song_data['urls']['catbox'].keys()]))
                    agg_data[curr_annid]['url of last wrong'] = song_data['urls']['catbox'][max_res]
    return agg_data


def convert_to_df(data):
    pd_data = {
        'ann id' : list(data.keys()),
        'show name' : [data[annid]['show name'] for annid in data],
        'in list?' : [data[annid]['in list?'] for annid in data],
        'date last correct' : [data[annid]['date last correct'] for annid in data],
        'date last wrong' : [data[annid]['date last wrong'] for annid in data],
        'number correct' : [data[annid]['number correct'] for annid in data],
        'number wrong' : [data[annid]['number wrong'] for annid in data],
        'total number seen' : [data[annid]['total number seen'] for annid in data],
        'song of last correct' : [data[annid]['song of last correct'] for annid in data],
        'url of last correct' : [data[annid]['url of last correct'] for annid in data],
        'song of last wrong' : [data[annid]['song of last wrong'] for annid in data],
        'url of last wrong' : [data[annid]['url of last wrong'] for annid in data],
    }
    return pd.DataFrame(data=pd_data)


if __name__ == '__main__':
    print('Hey hey hey start dash!')
    opts, args = getopt.getopt(sys.argv[1:], '', ['username=', 'min-date=', 'data='])
    username = ''
    min_date = (datetime.today() - timedelta(weeks=7)).strftime('%Y-%m-%d')
    datadir = '../amq/data/general'
    for o, a in opts:
        if o == '--username':
            username = a
        elif o == '--min-date':
            min_date = a
        elif o == 'data':
            datadir = a
    if username == '':
        print('Missing username or min date or data directory path!', file=sys.stderr)
        sys.exit(1) 
    print('Looking at data for', username)

    data = load_data_in_dir(min_date, username, datadir)
    df = convert_to_df(data)
    df.to_excel('all_song_overview.xlsx')
    print(df)

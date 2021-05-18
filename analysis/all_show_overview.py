import getopt
import json
import os
import pandas as pd
import sys
from datetime import datetime, timedelta
from Utils import get_filenames_in_order

def parse_file(filename, date, username, agg_data):
    # load json file
    file = open(filename, encoding='utf-8')
    json_data = json.load(file, encoding='utf-8')
    file.close()
    print('Loading file:', filename)

    # iterate through all song data. Assumes that later songs show up later.
    # agg_data = {}
    for song_data in json_data:
        curr_annid = song_data['annId']

        # check if show exists or not
        if curr_annid not in agg_data:
            agg_data[curr_annid] = {'show name': song_data['anime']['romaji'],
                                    'in list?' : True,
                                    'correct streak' : 0,
                                    'number correct' : 0, 
                                    'number wrong' : 0,
                                    'total number seen' : 0,
                                    'song of last correct' : '', 'url of last correct' : '',
                                    'song of last wrong' : '', 'url of last wrong' : '',
                                    'date last correct' : '', 'date last wrong': ''}
        
        # get player data
        player_data = [player_data for player_data in song_data['players'] if player_data['name'].lower() == username.lower()]
        if(len(player_data) == 0): continue
        player_data = player_data[0]
        
        # handle correct / wrong data
        max_res = str(max([int(num) for num in song_data['urls']['catbox'].keys()]))
        if player_data['correct']:
            agg_data[curr_annid]['number correct'] += 1
            agg_data[curr_annid]['song of last correct'] = song_data['name']
            agg_data[curr_annid]['url of last correct'] = song_data['urls']['catbox'][max_res]
            agg_data[curr_annid]['date last correct'] = date
            agg_data[curr_annid]['correct streak'] = 1 if agg_data[curr_annid]['correct streak'] <= 0 \
                                                                    else agg_data[curr_annid]['correct streak'] + 1
        else:
            agg_data[curr_annid]['number wrong'] += 1
            agg_data[curr_annid]['song of last wrong'] = song_data['name']
            agg_data[curr_annid]['url of last wrong'] = song_data['urls']['catbox'][max_res]
            agg_data[curr_annid]['date last wrong'] = date
            agg_data[curr_annid]['correct streak'] = -1 if agg_data[curr_annid]['correct streak'] >= 0 \
                                                                    else agg_data[curr_annid]['correct streak'] - 1
        agg_data[curr_annid]['total number seen'] += 1

        # get player list data
        list_check_count = len([True for list_data in song_data['fromList'] if list_data['name'].lower() == username.lower()])
        list_check = True if list_check_count == 1 else False
        agg_data[curr_annid]['in list?'] = list_check
    return agg_data
    
def make_report(date_files, username):
    agg_data = {}
    for date, filename in date_files:
        agg_data = parse_file(filename, date, username, agg_data)

    # convert to df
    pd_data = {
        'ANN ID' : list(agg_data.keys()),
        'Show Name' : [agg_data[annid]['show name'] for annid in agg_data],
        'In List?' : [agg_data[annid]['in list?'] for annid in agg_data],
        'Correct Streak' : [agg_data[annid]['correct streak'] for annid in agg_data],
        'Number Correct' : [agg_data[annid]['number correct'] for annid in agg_data],
        'Number Wrong' : [agg_data[annid]['number wrong'] for annid in agg_data],
        'Total Number Seen' : [agg_data[annid]['total number seen'] for annid in agg_data],
        'date last correct' : [agg_data[annid]['date last correct'] for annid in agg_data],
        'date last wrong' : [agg_data[annid]['date last wrong'] for annid in agg_data],
        'song of last correct' : [agg_data[annid]['song of last correct'] for annid in agg_data],
        'url of last correct' : [agg_data[annid]['url of last correct'] for annid in agg_data],
        'song of last wrong' : [agg_data[annid]['song of last wrong'] for annid in agg_data],
        'url of last wrong' : [agg_data[annid]['url of last wrong'] for annid in agg_data]
    }
    df = pd.DataFrame(data=pd_data)
    df = df.set_index(['ANN ID', 'Show Name'])

    # save as excel sheet
    df.to_excel('all_song_overview.xlsx')
    
    return df


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

    data_files = get_filenames_in_order(datadir)
    df = make_report(data_files, username)
    print(df[['In List?', 'Correct Streak']])

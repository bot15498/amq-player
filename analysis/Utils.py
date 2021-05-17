import re
import datetime
import os

def get_filenames_in_order(datadir: str='../amq/data/general'):
    # gets list of files in the order they were played.
    # uses date/timestamp on file if it's there, otherwise use modified time.
    # ordered by oldest to newest.
    all_filenames = []
    pattern = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}')
    for path, _, filenames in os.walk(datadir):
        for filename in filenames:
            if filename.split('.')[-1] == 'json':
                result = pattern.search(filename)
                if result:
                    date_str = result.group(0)
                    filetime = datetime.datetime.strptime(date_str,'%Y-%m-%d_%H-%M-%S')
                    all_filenames.append((filetime,path + '/' + filename))
                else:
                    # use modified time
                    filetime = datetime.fromtimestamp(os.path.getmtime(path + '/' + filename))
                    all_filenames.append((filetime,path + '/' + filename))
    
    # now sort
    sorted_filenames = sorted(all_filenames, key=lambda tup : tup[0])
    return sorted_filenames


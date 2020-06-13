import sys
import os
import tables
import collections
import time
import json
import numpy as np


def get_song(file_name, data_dict, verbose=True):
    '''get song data from h5'''
    start_t = time.time()
    h5 = tables.open_file(file_name, mode='r')
    path = h5.root
    file = file_name.split('/')[-1]

    # get all leaf in h5 tree
    for leaf in path._f_walknodes('Leaf'):
        # extract data from table
        if 'Table' in str(leaf):
            group, table = str(leaf)[1:].split('(')[0].split('/')
            for name in eval('h5.root.' + group + '.' + table + '.colnames'):
                entry = eval('h5.root.' + group + '.' + table + '.cols.' + name + '[0]')
                # deal with not JSON serializable data
                if isinstance(entry, np.integer):
                    entry = int(entry)
                elif isinstance(entry, np.bytes_):
                    entry = entry.decode('UTF-8')
                data_dict[file][str(group) + '/' + str(name)] = entry
        # extract other data
        else:
            group, arr = str(leaf)[1:].split('(', 1)[0].split('/')
            entry = list(eval('h5.root.' + group + '.' + arr + '[:]'))
            # deal with not JSON serializable data
            if len(entry) > 0 and isinstance(entry[0], np.ndarray):
                entry = [list(e) for e in entry]
            elif len(entry) > 0 and isinstance(entry[0], np.bytes_):
                entry = [e.decode('UTF-8') for e in entry]
            elif len(entry) > 0 and isinstance(entry[0], np.integer):
                entry = [int(e) for e in entry]
            data_dict[file][str(group) + '/' + str(arr)] = entry

    h5.close()

    if verbose:
        print(file, 'is converted. Time used: ', time.time() - start_t)


    return data_dict


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Please indicate input and output directories')

    path = sys.argv[1]
    output_dir = sys.argv[2]

    # checkpoint
    visited = set([f[:-5] for f in os.listdir(output_dir) if f.endswith('.json')])
    print(visited)

    # walk through input dir and get all file names
    files = collections.defaultdict(list)
    for (dir_path, dir_names, file_names) in os.walk(path):
        for file_name in file_names:
            if file_name.endswith('.h5'):
                files[dir_path].append(os.sep.join([dir_path, file_name]))

    # convert h5 to json
    for directory in files.keys():
        output_file_name = ''.join( ''.join(directory.split('data/')[1:]).split('/') )
        if output_file_name not in visited:
            for f in files[directory]:
                print(f)
                songs_dict = collections.defaultdict(dict)
                songs = get_song(f, songs_dict, verbose=False)

            json_file = str(output_dir) + '/' + str(output_file_name) + '.json'
            with open(json_file, 'w') as output:
                json.dump(songs_dict, output)
            print(json_file, ' completed!')

            # update checkpoint
            visited.add(output_file_name)
            
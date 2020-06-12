import sys
import csv
import json
from datetime import datetime

# def get_duration(row_number):
#     '''get workout duration (end time - start time)'''
#     start_time = datetime.fromtimestamp(data[row_number]['timestamp'][0])
#     end_time = datetime.fromtimestamp(data[row_number]['timestamp'][-1])
#     print('Start time is: ' + start_time)
#     print('End time is: ' + end_time)
#     print('Duration: ', end_time - start_time)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Input error!')
    
    input_json_path = sys.argv[1]
    output_csv_path = sys.argv[2]

    # read json to list of dict
    data = []
    with open(input_json_path) as f:
        for l in f:
            data.append(eval(l))
    print('Input {} file with length {}.'.format(input_json_path, len(data)))
    
    # check keys
    keys = data[0].keys()
    print('Keys: ', keys)
    
    # write to csv
    with open(output_csv_path, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


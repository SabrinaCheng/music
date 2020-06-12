import sys
import csv
import collections
import time

'''Instead of reading heart beat data from S3, 
the program gets data from ec2 to avoid memory error or "killed".''' 

def get_n_lines(file):
    '''get number of lines in the csv'''
    start_t = time.time()
    with open(file) as f:
        # get number of lines
        n_lines = sum(1 for line in f)
    print('Time used: {:.2f}'.format(time.time() - start_t))
    return n_lines


def read_firrec_data(file, block_size):
    '''read csv by batch size'''
    start_t = time.time()
    data = collections.defaultdict(dict)
    with open(file) as f:
        # init csv reader
        reader = csv.reader(f)
        # get header
        header = next(reader)
        print('Columns: ', header)
        # read lines
        for i in range(n_lines - 1):
            block_idx = i // block_size
            # create a new block
            if i % block_size == 0:
                print('Create block #{}'.format(block_idx))
                for col in header:
                    data['Block_' + str(block_idx)][col] = []
            row = next(reader)
            for idx, col in enumerate(header):
                data['block_' + str(block_idx)][col].append(row[idx])
    print('Time used: {:.2f}'.format(time.time() - start_t))


    return data


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print('Please give a csv path')
    
    file = sys.argv[1]
    block_size = 10000

    n_lines = get_n_lines(file)
    print('Number of lines:', n_lines)
    workout_data = read_firrec_data(file, block_size)

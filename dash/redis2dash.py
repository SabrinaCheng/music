import sys
import dash_core_components
import redis



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Please enter Redis password')

    password = sys.argv[1]

    # connect to Redis
    r = redis.Redis(
        host='ec2-34-219-119-131.us-west-2.compute.amazonaws.com',
        port=6379, 
        password=password)
    
    for k in r.keys():
        print(k)

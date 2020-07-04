import json
import boto3
import sys
import resource
def using(point=""):
    usage=resource.getrusage(resource.RUSAGE_SELF)
    return '''%s: usertime=%s systime=%s mem=%s mb
           '''%(point,usage[0],usage[1],
                usage[2]/1024.0 )

print(using("before"))

bucket = 'fitrec'
key = 'proper/endomondoHR_proper.json'

# s3 = boto3.resource('s3')
# obj = s3.Object(bucket, key)
# print('size of obj', sys.getsizeof(obj))
# data = json.dumps(obj.get()['Body']).decode('utf-8')
# print('size of data', sys.getsizeof(data))
# print('Finished!')

s3 = boto3.client('s3')
obj = s3.get_object(Bucket=bucket, Key=key)
print('size of obj', sys.getsizeof(obj))
file_content = obj['Body'].read().decode('utf-8').splitlines(True)
print('size of file_content', sys.getsizeof(file_content))
# i = 0
for line in file_content:
    pass
    # print(line)
    # i += 1
    # if i == 3: break


print(using("after"))
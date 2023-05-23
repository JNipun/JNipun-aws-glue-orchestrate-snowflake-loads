import sys
import boto3
import json
from snowflake import connector
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv, ['AWS_JOB_NAME', 'ACCOUNT', 'WAREHOUSE', 'ROLE', 'DATABASE', 'SCHEMA', 'URL', 'AWS_SECRET_NAME', 'AWS_REGION_NAME', 'STORED_PROC_NM'])

client = boto3.client("secretsmanager", region_name=args['AWS_REGION_NAME'])
get_secret_value_response = client.get_secret_value(SecretId=args['AWS_SECRET_NAME'])
secret = get_secret_value_response['SecretString']
secret = json.loads(secret)
user = secret.get('user')
password = secret.get('password')


try:            
    conn = connector.connect(account=args['ACCOUNT'],
                             user=user,
                             password=password,
                             role=args['ROLE'],
                             warehouse=args['WAREHOUSE'],
                             database=args['DATABASE'],
                             url=args['URL'],
                             autocommit=True)
    cursor = conn.cursor()             
    query = "call " + args['DATABASE'] + '.' + args['SCHEMA'] + '.' + args['STORED_PROC_NM'] + " ;"
    print(query)
    cursor.execute(query)       
    data = cursor.fetchone()
    print(data)                       

except Exception as e:
    print(e)

import boto3


print("🚀 Script started")

try:
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('login')
    print(f"✅ Connected to table: {table.name}")
except Exception as e:
    print("❌ Error creating DynamoDB resource or table:", e)

# Change region if needed
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# This must exactly match the table name in AWS
table = dynamodb.Table('Login')
def test_read():
    try:
        response = table.scan()
        print("✅ Successfully scanned table")
        for item in response['Items']:
            print(item)
    except Exception as e:
        print("❌ Error during scan:", e)

test_read()

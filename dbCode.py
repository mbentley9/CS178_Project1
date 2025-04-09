import boto3

TABLE_NAME = "Login"  
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

def print_log(log_dict):
    print("Username: ", log_dict["Title"])
    print("Password: ", end="")
    print()

def create_movie():
    Username = input("Enter the username: ")
    Password = input("Enter your password: ")



    info = {
        "Username": Username if Username else None,
        "Password": Password if Password else None,
    }

    try:
        table.put_item(Item=info)
        print("Login was created successfully!")
    except Exception as e:
        print(f"Error creating Login: {e}")
        
def print_menu():
    print("----------------------------")
    print("Press C: to CREATE a new Login")
    print("Press X: to EXIT application")
    print("----------------------------")

def main():
    input_char = ""
    while input_char.upper() != "X":
        print_menu()
        input_char = input("Choice: ")
        if input_char.upper() == "C":
            create_movie()
        elif input_char.upper() == "X":
            print("Exiting...")
        else:
            print("Not a valid option. Try again.")
main()

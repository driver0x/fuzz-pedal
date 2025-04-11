import logging
from account_generator import generate_account
from profile_generator import create_name, create_password

def main():
    amount = int(input("how many accounts? "))
    for i in range(amount):
        print(f"Generating account {i+1} of {amount}")
        password = create_password()
        email = generate_account(name=create_name(), password=password, talents=["Other"], genres=["Other"], artists=["Taylor Swift"])
        combo = f"{email[0]}:{password}:{email[1]}:{email[2]}"
        print(f"Created account: {combo}")
        with open("accounts.txt", "a") as file:
            file.write(combo + "\n")
    print("Task complete.")

if __name__ == "__main__":
    logging.basicConfig(filename='crash.log', level=logging.ERROR, filemode="w")
    try:
        main()
    except Exception as e:
        logging.exception(e)
        print("An error occured. Check crash.log")
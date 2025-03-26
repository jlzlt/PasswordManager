import config
import logging
from auth import AuthManager
from database import DatabaseManager
from encryption import EncryptionManager
from passwords_manager import PasswordsManager

def main():
    db = DatabaseManager()
    auth = AuthManager()

    action = input("Register or Login? ").lower()

    if action == "register":
        register_username = input("Username: ")
        register_password = input("Password: ")
        print(auth.register_user(register_username, register_password))
        login_username = input("Login with Username: ")
        login_password = input("Login with Password: ")
        print(auth.login_user(login_username, login_password))
    elif action == "login":
        login_username = input("Username: ")
        login_password = input("Password: ")
        print(auth.login_user(login_username, login_password))

    print(auth.current_user)

    user = db.execute_query("SELECT * FROM users WHERE user_id = ?", (auth.current_user,))[0]

    print(f"""
Username: {user["username"]}
Password: {user["password"]}
Key salt: {user["key_salt"]}
Encryption key: {user["encryption_key"]}
          """)

    pwman = PasswordsManager(login_password, user["key_salt"], user["encryption_key"], auth.current_user)

    while True:

        action2 = input("""
change username
change password
add
retrieve
update website
update username
update password
update comment
delete
list
quit

Your action: """).lower()

        if action2 == "change password":
            old_password = input("Old password: ")
            new_password = input("New password: ")
            return_value = auth.change_password(old_password, new_password)
            if return_value == "Password changed successfully.":
                pwman.user_password = new_password
            print(return_value)

        elif action2 == "change username":
            new_username = input("New username: ")
            print(auth.change_username(new_username))

        elif action2 == "add":
            website = input("Website: ")
            username = input("Username: ")
            password = input("Password: ")
            comment = input("Comment: ")

            print(pwman.add_entry(website, username, password, comment))

        elif action2 == "retrieve":
            entry_id = input("Entry ID: ")
            entry = pwman.retrieve_entry(entry_id)
            print(entry)

        elif action2 == "update website":
            entry_id = input("Entry ID: ")
            new_website = input("New website: ")
            print(pwman.update_website(entry_id, new_website))

        elif action2 == "update username":
            entry_id = input("Entry ID: ")
            new_username = input("New username: ")
            print(pwman.update_username(entry_id, new_username))

        elif action2 == "update password":
            entry_id = input("Entry ID: ")
            new_password = input("New password: ")
            print(pwman.update_password(entry_id, new_password))

        elif action2 == "update comment":
            entry_id = input("Entry ID: ")
            new_comment = input("New comment: ")
            print(pwman.update_comment(entry_id, new_comment))

        elif action2 == "delete":
            entry_id = input("Entry ID: ")
            print(pwman.delete_entry(entry_id))

        elif action2 == "list":
            list = pwman.list_entries(auth.current_user)
            for item in list:
                print(item)

        elif action2 == "quit":
            break


if __name__ == "__main__":
    main()

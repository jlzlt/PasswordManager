import customtkinter as ctk
import tkinter as tk
from database import DatabaseManager
from auth import AuthManager
from passwords_manager import PasswordsManager

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class PasswordManagerGUI:
    def __init__(self, root):     
        self.root = root
        self.root.title("Password Manager")
        self.center_window(300, 250)  

        # Configure grid weights for the root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Login page
        self.login_frame = ctk.CTkFrame(self.root)
        self.login_frame.grid(row=0, column=0, padx=20, pady=20)

        # Username label and entry
        self.username_label = ctk.CTkLabel(self.login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, padx=(20,5), pady=(20,5))
        self.username_entry = ctk.CTkEntry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=(5, 20), pady=(20,5))

        # Password label and entry
        self.password_label = ctk.CTkLabel(self.login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, padx=(20,5), pady=5)
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=(5,20), pady=5)

        # Login button
        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=(10, 5))

        # Register button
        self.login_button = ctk.CTkButton(self.login_frame, text="Register", command=self.register)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=5)

        # Error label
        self.error_label = ctk.CTkLabel(self.login_frame, text="")
        self.error_label.grid(row=4, column=0, columnspan=2, pady=5)

        # AuthManager instance for login
        self.auth = AuthManager()
        self.db = DatabaseManager()
        self.pwman = None

        self.root.bind("<Return>", lambda event: self.login())

    def center_window(self, width=300, height=300):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        login_status = self.auth.login_user(username, password)

        if login_status == "Login successful.":
            user = self.db.execute_query("SELECT * FROM users WHERE user_id = ?", (self.auth.current_user,))[0]
            self.pwman = PasswordsManager(password, user["key_salt"], user["encryption_key"], self.auth.current_user)
            self.login_frame.destroy()
            self.open_dashboard()
        else:
            self.error_label.configure(text=login_status)

    def register(self):
        pass

    def open_dashboard(self):
        self.center_window(600, 600)
        user = self.db.execute_query("SELECT * FROM users WHERE user_id = ?", (self.auth.current_user,))[0]     
        self.root.title(f"Password Manager - Dashboard - User: {user['username']}")
        # Setup the dashboard after Login
        self.dashboard_frame = ctk.CTkFrame(self.root)
        self.dashboard_frame.pack(padx=20, pady=20)

        self.username2_label = ctk.CTkLabel(self.dashboard_frame, text=f"Welcome, {user['username']}!")
        self.username2_label.grid(row=0, column=0, padx=5, pady=5)

        self.add_password_button = ctk.CTkButton(self.dashboard_frame, text="Add Password", command=self.add_password)
        self.add_password_button.grid(row=0, column=1, padx=5, pady=5)

        self.change_password_button = ctk.CTkButton(self.dashboard_frame, text="Change Password", command=self.change_password)
        self.change_password_button.grid(row=1, column=1, padx=5, pady=5)

        self.list_passwords_button = ctk.CTkButton(self.dashboard_frame, text="List Passwords", command=self.list_passwords)
        self.list_passwords_button.grid(row=2, column=1, padx=5, pady=5)

        self.list_passwords()

    def list_passwords(self):
        for widget in self.dashboard_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                continue
            widget.destroy()  # Clear previous widgets before updating

        passwords = self.pwman.list_entries(self.auth.current_user)

        if passwords:
            row = 0
            for pw in passwords:
                label = ctk.CTkLabel(self.dashboard_frame, text=f"{pw['website']} - {pw['username']}")
                label.grid(row=row, column=2, padx=5, pady=5)
                row += 1
        else:
            label = ctk.CTkLabel(self.dashboard_frame, text="No passwords stored.")
            label.grid(row=0, column=2, padx=5, pady=5)

    def add_password(self):
        pass

    def change_password(self):
        pass


if __name__ == "__main__":
    root = ctk.CTk()
    gui = PasswordManagerGUI(root)
    root.mainloop()

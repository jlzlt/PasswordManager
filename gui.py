import customtkinter as ctk
import tkinter as tk
from auth import AuthManager
from config import VERSION
from database import DatabaseManager
from passwords_manager import PasswordsManager
from PIL import Image


class PasswordManagerGUI:
    def __init__(self, root):     
        self.root = root
        self.center_window(400, 300)
        self.root.resizable(False, False)
        self.root.iconbitmap("static/padlock.ico")

        # Configure grid weights for the root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.index_font = ctk.CTkFont(family="Roboto", size=16)
        self.entry_font = ctk.CTkFont(family="Roboto", size=14)
        self.button_font = ctk.CTkFont(family="Roboto", size=16, weight="bold")
        self.error_font = ctk.CTkFont(family="Roboto", size=14)

        # Initialize frames for login and registration
        self.login_frame = ctk.CTkFrame(self.root)
        self.register_frame = ctk.CTkFrame(self.root)

        self.create_login_frame()
        self.create_register_frame()

        self.auth = AuthManager()
        self.db = DatabaseManager()
        self.pwman = None

        # Initially show login frame
        self.show_login_frame()

    def create_login_frame(self):
        login_image = ctk.CTkImage(Image.open("static/login3.png"), size=(20, 20))

        # Login page widgets
        self.username_label = ctk.CTkLabel(self.login_frame, font=self.index_font, text="Username:")
        self.username_label.grid(column=0, row=0, padx=(20,5), pady=(20,5))
        self.username_entry = ctk.CTkEntry(self.login_frame, font=("Roboto", 14))
        self.username_entry.grid(row=0, column=1, padx=(5, 20), pady=(20,5))

        self.password_label = ctk.CTkLabel(self.login_frame, text="Password:", font=self.index_font)
        self.password_label.grid(row=1, column=0, padx=(20,5), pady=5)
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", font=self.entry_font)
        self.password_entry.grid(row=1, column=1, padx=(5,20), pady=5)

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.login, font=self.button_font, image=login_image)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=(20, 5))

        self.register_button = ctk.CTkButton(self.login_frame, text="Register", command=self.show_register_frame, font=self.button_font)
        self.register_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.error_label = ctk.CTkLabel(self.login_frame, text="", font=self.error_font)
        self.error_label.grid(row=4, column=0, columnspan=2, pady=10)

    def create_register_frame(self):
        register_image = ctk.CTkImage(Image.open("static/register.png"), size=(20, 20))

        # Registration page widgets
        self.username_reg_label = ctk.CTkLabel(self.register_frame, text="Username:", font=self.index_font)
        self.username_reg_label.grid(row=0, column=0, padx=(20,5), pady=(20,5))
        self.username_reg_entry = ctk.CTkEntry(self.register_frame, font=self.entry_font)
        self.username_reg_entry.grid(row=0, column=1, padx=(5, 20), pady=(20,5))

        self.password_reg_label = ctk.CTkLabel(self.register_frame, text="Password:", font=self.index_font)
        self.password_reg_label.grid(row=1, column=0, padx=(20,5), pady=5)
        self.password_reg_entry = ctk.CTkEntry(self.register_frame, show="*", font=self.entry_font)
        self.password_reg_entry.grid(row=1, column=1, padx=(5,20), pady=5)

        self.repassword_reg_label = ctk.CTkLabel(self.register_frame, text="Re-Enter Password:", font=self.index_font)
        self.repassword_reg_label.grid(row=2, column=0, padx=(20,5), pady=5)
        self.repassword_reg_entry = ctk.CTkEntry(self.register_frame, show="*", font=self.entry_font)
        self.repassword_reg_entry.grid(row=2, column=1, padx=(5,20), pady=5)

        self.register_submit_button = ctk.CTkButton(self.register_frame, text="Register", command=self.register, font=self.button_font, image=register_image)
        self.register_submit_button.grid(row=3, column=0, columnspan=2, pady=(20, 5))

        self.back_to_login_button = ctk.CTkButton(self.register_frame, text="Back to Login", command=self.show_login_frame, font=self.button_font)
        self.back_to_login_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.error_reg_label = ctk.CTkLabel(self.register_frame, text="", font=self.error_font)
        self.error_reg_label.grid(row=5, column=0, columnspan=2, pady=10)

    def show_login_frame(self):
        # Change window title for login
        self.root.title("Password Manager - Login")

        # Hide registration frame and show login frame
        self.register_frame.grid_forget()
        self.error_label.configure(text="")
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')        

        self.login_frame.grid(row=0, column=0, padx=20, pady=20)
        self.login_frame.configure(fg_color="transparent")

        self.root.bind("<Return>", lambda event: self.login())

    def show_register_frame(self):
        # Change window title for registration
        self.root.title("Password Manager - Register")

        # Hide login frame and show registration frame
        self.login_frame.grid_forget()
        self.error_reg_label.configure(text="")
        self.username_reg_entry.delete(0, 'end')
        self.password_reg_entry.delete(0, 'end')
        self.repassword_reg_entry.delete(0, 'end')
        self.register_frame.grid(row=0, column=0, padx=20, pady=20)
        self.register_frame.configure(fg_color="transparent")

        self.root.bind("<Return>", lambda event: self.register())

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
            self.register_frame.destroy()
            self.root.unbind("<Return>")
            self.open_dashboard()
        else:
            self.error_label.configure(text=login_status)

    def logout(self):
        pass

    def register(self):
        username = self.username_reg_entry.get()
        password = self.password_reg_entry.get()
        repassword = self.repassword_reg_entry.get()

        register_status = self.auth.register_user(username, password, repassword)

        if register_status == "Registration successful.":            
            self.show_login_frame(self)
        else:
            self.error_reg_label.configure(text=register_status)

    def open_dashboard(self):
        self.center_window(600, 600)
        self.root.resizable(True, True)
        user = self.db.execute_query("SELECT * FROM users WHERE user_id = ?", (self.auth.current_user,))[0]     
        self.root.title(f"Password Manager - Dashboard - User: {user['username']}")
        # Setup the dashboard after Login
        self.dashboard_frame = ctk.CTkFrame(self.root)
        self.dashboard_frame.grid(row=0, column=0, padx=20, pady=20)
        self.dashboard_frame.configure(fg_color="transparent")

        self.username2_label = ctk.CTkLabel(self.dashboard_frame, text=f"Welcome!", font=("Arial", 20))
        self.username2_label.grid(row=0, column=0, padx=5, pady=5, columnspan=2)

        self.add_password_button = ctk.CTkButton(self.dashboard_frame, text="Add Password", command=self.add_password)
        self.add_password_button.grid(row=1, column=0, padx=5, pady=5)

        self.change_password_button = ctk.CTkButton(self.dashboard_frame, text="Change Password", command=self.change_password)
        self.change_password_button.grid(row=2, column=0, padx=5, pady=5)

        self.list_passwords_button = ctk.CTkButton(self.dashboard_frame, text="List Passwords", command=self.list_passwords)
        self.list_passwords_button.grid(row=3, column=0, padx=5, pady=5)

        self.logout_button = ctk.CTkButton(self.dashboard_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=4, column=0, padx=5, pady=5)

        self.test_button = ctk.CTkButton(self.dashboard_frame, text="Test", fg_color="transparent", border_width=1, border_color="gray", hover_color="gray30")
        self.test_button.grid(row=5, column=0, padx=5, pady=5)

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
                label.grid(row=(6 + row), column=0, padx=5, pady=5, columnspan=2)
                row += 1
        else:
            label = ctk.CTkLabel(self.dashboard_frame, text="No passwords stored.")
            label.grid(row=6, column=0, padx=5, pady=20, columnspan=2)

    def add_password(self):
        pass

    def change_password(self):
        pass


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    gui = PasswordManagerGUI(root)
    root.mainloop()

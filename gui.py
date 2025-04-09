import customtkinter as ctk
import gc
import pandas as pd
import threading
import tkinter as tk
import webbrowser
from auth import AuthManager
from config import VERSION
from CTkMessagebox import CTkMessagebox
from database import DatabaseManager
from password_generator import PasswordGenerator
from passwords_manager import PasswordsManager
from PIL import Image


class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.center_window(400, 300)
        self.root.resizable(False, False)
        self.root.iconbitmap("static/padlock.ico")

        # This is for handling delete confirmation box
        self.selected_pass_name = None
        self.pass_frame_cache = {}

        # Configure grid weights for the root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self._init_style()

        # Initialize frames for login and registration
        self.login_frame = ctk.CTkFrame(self.root)
        self.register_frame = ctk.CTkFrame(self.root)

        self.create_login_frame()
        self.create_register_frame()

        self.auth = AuthManager()
        self.db = DatabaseManager()
        self.passgen = PasswordGenerator()
        self.pwman = None

        # Initially show login frame
        self.show_login_frame()

    def _init_style(self):
        self.font_index = ctk.CTkFont(family="Roboto", size=16)
        self.font_normal = ctk.CTkFont(family="Roboto", size=16)
        self.font_entry = ctk.CTkFont(family="Roboto", size=14)
        self.font_bigbutton = ctk.CTkFont(family="Roboto", size=16, weight="bold")
        self.font_button = ctk.CTkFont(family="Roboto", size=14, weight="bold")
        self.font_std_button = ctk.CTkFont(family="Roboto", size=14)
        self.font_error = ctk.CTkFont(family="Roboto", size=14, slant="italic")
        self.font_help = ctk.CTkFont(family="Roboto", size=14)
        self.font_help_del = ctk.CTkFont(family="Roboto", size=14)
        self.font_pass_name = ctk.CTkFont(family="Roboto", size=16, weight="bold")
        self.font_dash = ctk.CTkFont(family="Roboto", size=16)
        self.font_title = ctk.CTkFont(family="Roboto", size=24, weight="bold")
        self.font_footer = ctk.CTkFont(family="Roboto", size=14)

        # #008B8B
        self.bcolor_container = "#722F37"
        self.bcolor_passContainer = "#722F37"
        self.bcolor_passEntryContainer = "#722F37"
        self.bcolor_separator = "#DEA193"
        self.bcolor_pass_name = "black"

        self.corrad_tools = 50
        self.corrad_main_container = 25
        self.corrad_containers = 25
        self.corrad_separator = 100
        self.corrad_pass_name = 50
        self.corrad_normal_btn = 10

        self.width_separator = 3
        self.width_container = 2
        self.width_passContainer = 2

        self.color_tools_btn = "transparent"
        self.color_tools_btn_hover = "#06402B"
        self.color_tools_btn_selected = "#06402B"
        self.color_pass_name = "transparent" # "#1f538d"
        self.color_pass_name_hover = "#06402B" # "#14375e"
        self.color_pass_name_selected = "#06402B" # "#14375e"

###### <<<<<<<<<<<<<<<<<<<< Login/Register >>>>>>>>>>>>>>>>>>>> #####

    def create_login_frame(self):
        login_image = ctk.CTkImage(Image.open("static/login3.png"), size=(20, 20))

        # Login page widgets
        self.username_label = ctk.CTkLabel(self.login_frame, font=self.font_index, text="Username:")
        self.username_label.grid(column=0, row=0, padx=(20,5), pady=(20,5))
        self.username_entry = ctk.CTkEntry(self.login_frame, 
                                           font=self.font_entry,
                                           corner_radius=10, 
                                           height=35)
        self.username_entry.grid(row=0, column=1, padx=(5, 20), pady=(20,5))        

        self.password_label = ctk.CTkLabel(self.login_frame, text="Password:", font=self.font_index)
        self.password_label.grid(row=1, column=0, padx=(20,5), pady=5)
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", font=self.font_entry, corner_radius=10, height=35)
        self.password_entry.grid(row=1, column=1, padx=(5,20), pady=5)

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.login, font=self.font_button, image=login_image)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=(20, 5))

        self.register_button = ctk.CTkButton(self.login_frame, text="Register", command=self.show_register_frame, font=self.font_button)
        self.register_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.error_label = ctk.CTkLabel(self.login_frame, text="", font=self.font_error)
        self.error_label.grid(row=4, column=0, columnspan=2, pady=10)

    def create_register_frame(self):
        register_image = ctk.CTkImage(Image.open("static/register.png"), size=(20, 20))

        # Registration page widgets
        self.username_reg_label = ctk.CTkLabel(self.register_frame, text="Username:", font=self.font_index)
        self.username_reg_label.grid(row=0, column=0, padx=(20,5), pady=(20,5))
        self.username_reg_entry = ctk.CTkEntry(self.register_frame, font=self.font_entry)
        self.username_reg_entry.grid(row=0, column=1, padx=(5, 20), pady=(20,5))

        self.password_reg_label = ctk.CTkLabel(self.register_frame, text="Password:", font=self.font_index)
        self.password_reg_label.grid(row=1, column=0, padx=(20,5), pady=5)
        self.password_reg_entry = ctk.CTkEntry(self.register_frame, show="*", font=self.font_entry)
        self.password_reg_entry.grid(row=1, column=1, padx=(5,20), pady=5)

        self.repassword_reg_label = ctk.CTkLabel(self.register_frame, text="Re-Enter Password:", font=self.font_index)
        self.repassword_reg_label.grid(row=2, column=0, padx=(20,5), pady=5)
        self.repassword_reg_entry = ctk.CTkEntry(self.register_frame, show="*", font=self.font_entry)
        self.repassword_reg_entry.grid(row=2, column=1, padx=(5,20), pady=5)

        self.register_submit_button = ctk.CTkButton(self.register_frame, text="Register", command=self.register, font=self.font_button, image=register_image)
        self.register_submit_button.grid(row=3, column=0, columnspan=2, pady=(20, 5))

        self.back_to_login_button = ctk.CTkButton(self.register_frame, text="Back to Login", command=self.show_login_frame, font=self.font_button)
        self.back_to_login_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.error_reg_label = ctk.CTkLabel(self.register_frame, text="", font=self.font_error)
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

        self.root.after(100, lambda: self.username_entry.focus_set())

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

        self.root.after(100, lambda: self.username_reg_entry.focus_set())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        login_status = self.auth.login_user(username, password)

        if login_status == "Login successful.":
            self.user = self.db.execute_query("SELECT * FROM users WHERE user_id = ?", (self.auth.current_user,))[0]
            self.pwman = PasswordsManager(password, self.user["key_salt"], self.user["encryption_key"], self.auth.current_user)
            self.login_frame.grid_forget()
            self.register_frame.grid_forget()
            self.root.unbind("<Return>")
            self.show_loading_screen()
        else:
            self.error_label.configure(text=login_status)

    def register(self):
        username = self.username_reg_entry.get()
        password = self.password_reg_entry.get()
        repassword = self.repassword_reg_entry.get()

        register_status = self.auth.register_user(username, password, repassword)

        if register_status == "Registration successful.":            
            self.show_login_frame()
        else:
            self.error_reg_label.configure(text=register_status)

###### <<<<<<<<<<<<<<<<<<<< Dashboard Loading Sequance >>>>>>>>>>>>>>>>>>>> #####

    def show_loading_screen(self):
        # Create a loading screen
        self.loading_frame = ctk.CTkFrame(self.root)
        self.loading_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.loading_frame.grid_rowconfigure(0, weight=1)
        self.loading_frame.grid_columnconfigure(0, weight=1)

        # Create a progress bar
        self.loading_progress = ctk.CTkProgressBar(self.loading_frame, width=300)
        self.loading_progress.grid(row=0, column=0, padx=20, pady=(20, 0))
        self.loading_progress.set(0)  # Start at 0%
        
        # Add a label below the progress bar
        self.loading_label = ctk.CTkLabel(self.loading_frame, text="Loading, please wait...", font=("Roboto", 16))
        self.loading_label.grid(row=1, column=0, padx=10, pady=(0, 20))
        
        # Create a variable to track loading state
        self.loading_state = {"progress": 0, "message": "Starting..."}
        
        # Force update the UI to show loading screen immediately
        self.root.update()
        
        # Start the loading process in a separate thread
        loading_thread = threading.Thread(target=self._background_loading_task)
        loading_thread.daemon = True  # Make thread terminate when main program exits
        loading_thread.start()
        
        # Start the progress update loop
        self._update_progress_ui()

    def _update_progress_ui(self):
        """Update the progress bar and message in the main thread"""
        self.loading_progress.set(self.loading_state["progress"])
        self.loading_label.configure(text=self.loading_state["message"])
        # Schedule another update if not completed
        if self.loading_state["progress"] < 1.0:
            self.root.after(100, self._update_progress_ui)

    def _background_loading_task(self):
        """Background task to handle all loading operations"""
        # Update progress - Starting
        self.loading_state = {"progress": 0.1, "message": "Initializing..."}
        
        # Create the dashboard and perform all setup
        self.loading_state = {"progress": 0.3, "message": "Creating dashboard..."}
        self._create_dashboard_frames()
        
        # Cache password data
        self.loading_state = {"progress": 0.6, "message": "Loading passwords..."}
        self.cache_all_passwords()
        
        # Final loading steps
        self.loading_state = {"progress": 0.9, "message": "Finalizing..."}
        
        # Schedule UI update to happen in the main thread
        self.root.after(0, self._complete_loading)

    def _create_dashboard_frames(self):
        """Create all dashboard frames without displaying them yet"""
        # This contains the UI creation logic from open_dashboard
        # but doesn't make anything visible yet
        self.main_container = ctk.CTkFrame(self.root)
        self.tools_main_frame = ctk.CTkFrame(self.main_container, fg_color="gray15")
        self.pass_container_frame = ctk.CTkFrame(self.main_container, border_color=self.bcolor_container, 
                                                border_width=self.width_container, fg_color="transparent", corner_radius=self.corrad_main_container)
        self.passgen_container_frame = ctk.CTkFrame(self.main_container, border_color=self.bcolor_container, 
                                                    border_width=self.width_container, fg_color="transparent", corner_radius=self.corrad_containers)
        self.outdata_container_frame = ctk.CTkFrame(self.main_container, border_color=self.bcolor_container, 
                                                    border_width=self.width_container, fg_color="transparent", corner_radius=self.corrad_containers)
        self.indata_container_frame = ctk.CTkFrame(self.main_container, border_color=self.bcolor_container, 
                                                   border_width=self.width_container, fg_color="transparent", corner_radius=self.corrad_containers)
        self.user_container_frame = ctk.CTkFrame(self.main_container, border_color=self.bcolor_container, 
                                                 border_width=self.width_container, fg_color="transparent", corner_radius=self.corrad_containers)
        self.stats_container_frame = ctk.CTkFrame(self.main_container, border_color=self.bcolor_container,
                                                  border_width=self.width_container, fg_color="transparent", corner_radius=self.corrad_containers)
        
        # Setup all the frames but don't grid them yet
        self.fill_tools_frame(self.user)
        self.fill_pass_frame(self.user)
        self.fill_pass_gen_frame()
        self.fill_export_data_frame()
        self.fill_import_data_frame()
        self.fill_user_frame()
        self.fill_statistics_frame()

    def _complete_loading(self):
        """Final step to hide loading screen and show dashboard"""
        # Set loading to complete
        self.loading_state = {"progress": 1.0, "message": "Complete!"}
        
        # Give a slight delay so users can see the completed progress bar
        self.root.after(500, self._show_dashboard)

    def _show_dashboard(self):
        """Show the dashboard after loading is complete"""
        # Hide loading screen
        self.loading_frame.grid_forget()
        
        # Center and resize the window
        self.center_window(1100, 700)
        self.root.resizable(True, True) 
        self.root.minsize(width=450, height=575)
        self.root.title(f"Password Manager - Dashboard - User: {self.user['username']}")
        
        # Grid the main container and configure it
        self.main_container.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=0)
        self.main_container.grid_columnconfigure(1, weight=1)
        
        # Grid the tools frame
        self.tools_main_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.tools_main_frame.grid_rowconfigure(1, weight=1)
        self.tools_main_frame.grid_columnconfigure(0, weight=1)
        
        # Grid the passwords container
        self.pass_container_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.pass_container_frame.grid_columnconfigure(0, weight=0)
        self.pass_container_frame.grid_columnconfigure(1, weight=1)
        self.pass_container_frame.grid_rowconfigure(0, weight=1)

        # Grid the password generator container
        self.passgen_container_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.passgen_container_frame.grid_columnconfigure(0, weight=1)
        self.passgen_container_frame.grid_rowconfigure(0, weight=0)  
        self.passgen_container_frame.grid_rowconfigure(1, weight=1)
        
        # Grid the export data container
        self.outdata_container_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.outdata_container_frame.grid_columnconfigure(0, weight=1)
        self.outdata_container_frame.grid_rowconfigure(1, weight=1)

        # Grid the import data container
        self.indata_container_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.indata_container_frame.grid_columnconfigure(0, weight=1)
        self.indata_container_frame.grid_rowconfigure(1, weight=1)

        # Grid the user container        
        self.user_container_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.user_container_frame.grid_columnconfigure(0, weight=1)
        self.user_container_frame.grid_rowconfigure(1, weight=1)
        
        # Grid the statistics container        
        self.stats_container_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.stats_container_frame.grid_columnconfigure(0, weight=1)
        self.stats_container_frame.grid_rowconfigure(1, weight=1)

        # Select default tool
        self.selected_tools_button(self.passwords_button)

    def fill_tools_frame(self, user):
        # Setup header, nav and footer frames
        width = 200

        self.tools_header_frame = ctk.CTkFrame(self.tools_main_frame, fg_color="transparent")
        self.tools_header_frame.grid(row=0, column=0, padx=10, pady=50, sticky="nwe")

        self.tools_header_frame.grid_columnconfigure(0, weight=1)

        self.tools_nav_frame = ctk.CTkFrame(self.tools_main_frame, fg_color="transparent")
        self.tools_nav_frame.grid(row=1, column=0, padx=10, sticky="nsew")

        self.tools_nav_frame.grid_columnconfigure(0, weight=1)

        self.tools_footer_frame = ctk.CTkFrame(self.tools_main_frame, fg_color="transparent")
        self.tools_footer_frame.grid(row=2, column=0, padx=10, pady=50, sticky="swe")

        self.tools_footer_frame.grid_columnconfigure(0, weight=1)

        # Fill header frame

        self.welcome_label = ctk.CTkLabel(self.tools_header_frame, text=f"Welcome, {user['username']}", font=self.font_title)
        self.welcome_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        self.tools_header_separator = ctk.CTkFrame(self.tools_header_frame, height=self.width_separator, corner_radius=self.corrad_separator, fg_color=self.bcolor_separator)
        self.tools_header_separator.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Fill nav frame

        self.passwords_button = ctk.CTkButton(self.tools_nav_frame, text="Passwords", font=self.font_bigbutton, width=width,
                                              command=lambda: self.selected_tools_button(self.passwords_button), corner_radius=self.corrad_tools, fg_color=self.color_tools_btn)
        self.passwords_button.grid(row=0, column=0, padx=5, pady=20)

        self.pass_gen_button = ctk.CTkButton(self.tools_nav_frame, text="Password Generator", font=self.font_bigbutton, width=width,
                                             command=lambda: self.selected_tools_button(self.pass_gen_button), corner_radius=self.corrad_tools)
        self.pass_gen_button.grid(row=1, column=0, padx=5, pady=5)

        self.import_data_button = ctk.CTkButton(self.tools_nav_frame, text="Import Data", font=self.font_bigbutton, width=width,
                                                command=lambda: self.selected_tools_button(self.import_data_button), corner_radius=self.corrad_tools)
        self.import_data_button.grid(row=2, column=0, padx=5, pady=5)

        self.export_data_button = ctk.CTkButton(self.tools_nav_frame, text="Export Data", font=self.font_bigbutton, width=width,
                                                command=lambda: self.selected_tools_button(self.export_data_button), corner_radius=self.corrad_tools)
        self.export_data_button.grid(row=3, column=0, padx=5, pady=5)

        self.statistics_button = ctk.CTkButton(self.tools_nav_frame, text="Statistics", font=self.font_bigbutton, width=width,
                                               command=lambda: self.selected_tools_button(self.statistics_button), corner_radius=self.corrad_tools)
        self.statistics_button.grid(row=4, column=0, padx=5, pady=5)

        # Fill footer frame

        self.user_button = ctk.CTkButton(self.tools_footer_frame, text="User (Settings)", font=self.font_bigbutton, width=width,
                                         command=lambda: self.selected_tools_button(self.user_button), corner_radius=self.corrad_tools)
        self.user_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
       
        self.logout_button = ctk.CTkButton(self.tools_footer_frame, text="Logout", fg_color="transparent", border_width=1, width=width,
                                         border_color="gray", hover_color=self.color_tools_btn_hover, font=self.font_bigbutton, command=self.logout, corner_radius=self.corrad_tools)
        self.logout_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Create a list of all tools buttons for segmented button navigation
        self.all_tools_buttons = [self.passwords_button, self.pass_gen_button, self.import_data_button, self.export_data_button, self.statistics_button, self.user_button]        

    def selected_tools_button(self, clicked_button):        
        # Update visuals
        for btn in self.all_tools_buttons:
            btn.configure(fg_color=self.color_tools_btn)  # Reset all buttons color
            btn.configure(hover_color=self.color_tools_btn_hover)  # Reset hover color
        clicked_button.configure(fg_color=self.color_tools_btn_selected)  # Highlight selected

        if clicked_button == self.passwords_button:
            self.passwords_dash()
        elif clicked_button == self.pass_gen_button:
            self.pass_gen_dash()
        elif clicked_button == self.import_data_button:
            self.import_data_dash()
        elif clicked_button == self.export_data_button:
            self.export_data_dash()
        elif clicked_button == self.statistics_button:
            self.statistics_dash()
        elif clicked_button == self.user_button:
            self.user_dash()  

###### <<<<<<<<<<<<<<<<<<<< Passwords >>>>>>>>>>>>>>>>>>>> #####

    def fill_pass_frame(self, user):

        # Create left frame for navigation (header, main and footer frames inside)

        self.pass_left_frame = ctk.CTkFrame(self.pass_container_frame, border_color=self.bcolor_passContainer, border_width=2, fg_color="transparent", corner_radius=self.corrad_containers)
        self.pass_left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.pass_left_frame.grid_rowconfigure(1, weight=1)
        self.pass_left_frame.grid_columnconfigure(0, weight=1)

        # Header for Passwords left frame

        self.pass_left_frame_header = ctk.CTkFrame(self.pass_left_frame, fg_color="transparent")
        self.pass_left_frame_header.grid(row=0, column=0, padx=5, pady=(40, 0), sticky="nsew")

        self.pass_left_frame_label = ctk.CTkLabel(self.pass_left_frame_header, text="Choose password", font=self.font_title)
        self.pass_left_frame_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.pass_left_frame_search = ctk.CTkEntry(self.pass_left_frame_header, font=self.font_entry, placeholder_text="Search", corner_radius=10)
        self.pass_left_frame_search.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.pass_left_frame_search.bind("<KeyRelease>", self.filter_password_buttons)

        button_frame = ctk.CTkFrame(self.pass_left_frame_header, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)

        self.pass_left_frame_az = ctk.CTkButton(button_frame, text="A-Z", width=1, command=lambda: self.populate_password_buttons("az"))
        self.pass_left_frame_az.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.pass_left_frame_za = ctk.CTkButton(button_frame, text="Z-A", width=1, command=lambda: self.populate_password_buttons("za"))
        self.pass_left_frame_za.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Main for Passwords left frame

        self.pass_left_frame_main = ctk.CTkScrollableFrame(self.pass_left_frame)
        self.pass_left_frame_main.grid(row=1, column=0, sticky="nsew", padx=5, pady=10)

        self.pass_left_frame_main.grid_columnconfigure(0, weight=1)

        # Footer for Passwords left frame

        self.pass_left_frame_footer = ctk.CTkFrame(self.pass_left_frame, fg_color="transparent")
        self.pass_left_frame_footer.grid(row=2, column=0, padx=5, pady=20, sticky="nsew")

        self.pass_left_frame_footer.grid_columnconfigure(0, weight=1)
        self.pass_left_frame_footer.grid_columnconfigure(1, weight=1)

        self.pass_left_frame_add = ctk.CTkButton(self.pass_left_frame_footer, text="Add", width=1, command=self.add_password)
        self.pass_left_frame_add.grid(row=0, column=0, padx=1, pady=5, sticky="nsew")

        self.pass_left_frame_delete = ctk.CTkButton(self.pass_left_frame_footer, text="Delete", width=1, command=self.delete_password)
        self.pass_left_frame_delete.grid(row=0, column=1, padx=1, pady=5, sticky="nsew")

        # Create right frame that shows selected passwords

        self.pass_right_frame = ctk.CTkFrame(self.pass_container_frame, border_color=self.bcolor_passContainer, border_width=2, fg_color="transparent", corner_radius=self.corrad_containers)
        self.pass_right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")       

        self.pass_right_frame.grid_rowconfigure(1, weight=1)
        self.pass_right_frame.grid_columnconfigure(0, weight=1)

        # Header for Passwords right frame

        self.pass_right_frame_header = ctk.CTkFrame(self.pass_right_frame, fg_color="transparent")
        self.pass_right_frame_header.grid(row=0, column=0, padx=5, pady=(40, 10), sticky="nsew")
        self.pass_right_frame_header.grid_columnconfigure(0, weight=1)

        self.pass_right_frame_header_label = ctk.CTkLabel(self.pass_right_frame_header, text="", font=self.font_title, anchor="w")
        self.pass_right_frame_header_label.grid(row=0, column=0, padx=25, pady=5, sticky="w")

        # Main for Passwords right frame

        self.pass_right_frame_main = ctk.CTkFrame(self.pass_right_frame, fg_color="transparent")
        self.pass_right_frame_main.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
        self.pass_right_frame_main.grid_rowconfigure(0, weight=1)
        self.pass_right_frame_main.grid_columnconfigure(0, weight=1) 
    
    def passwords_dash(self):
        # Clear whatever was shown before
        self.clear_frame(self.pass_left_frame_main)
        self.forget_frame_widgets(self.pass_right_frame_main)
        self.forget_frame_widgets(self.pass_right_frame_header)   
        self.selected_pass_name = None

        # Change title and raise main frame for passwords
        self.root.title(f"Password Manager - Dashboard - User: {self.user['username']} - Passwords")
     
        self.populate_password_buttons()

        # Bind arrow keys for navigation
        self.root.bind("<Down>", lambda event: self.navigate_password_list("down"))
        self.root.bind("<Up>", lambda event: self.navigate_password_list("up"))

        self.pass_container_frame.tkraise()

    def navigate_password_list(self, direction):
        """Navigate through password list using arrow keys"""
        # Get a list of all password names (assuming they're sorted in the order you want)
        password_names = list(self.all_passwords_buttons.keys())
        
        if not password_names:
            return  # No passwords to navigate
            
        # If no password is currently selected, select the first one
        if self.selected_pass_name is None:
            self.selected_passwords_button(password_names[0])
            return
            
        # Find the current index
        try:
            current_index = password_names.index(self.selected_pass_name)
        except ValueError:
            # If the selected password isn't in the list anymore, reset to first
            self.selected_passwords_button(password_names[0])
            return
            
        # Calculate the new index based on direction
        if direction == "down":
            new_index = min(current_index + 1, len(password_names) - 1)
        else:  # Up
            new_index = max(current_index - 1, 0)
            
        # Select the new password
        self.selected_passwords_button(password_names[new_index])
        
    def selected_passwords_button(self, clicked_name):        
        if clicked_name in self.all_passwords_buttons.keys():
            # Reset all buttons' colors
            for btn in self.all_passwords_buttons.values():
                btn.configure(fg_color=self.color_pass_name)  # Reset all buttons color

            # Highlight the clicked button
            self.selected_pass_name = clicked_name
            self.selected_pass_btn = self.all_passwords_buttons[clicked_name]
            self.selected_pass_btn.configure(fg_color=self.color_pass_name_selected)  # Highlight selected      
              
            # Call function to display selected password's details
            self.get_pass_tab(clicked_name)
            if clicked_name in self.pass_frame_cache:
                self.pass_frame_cache[clicked_name]._parent_canvas.yview_moveto(0.0)  
        else:
            pass

    def add_password(self):
        self.add_pass_win = ctk.CTkToplevel(self.root)
        self.add_pass_win.title("Add a password")        
        new_window_width = 400
        new_window_height = 350
        x_offset, y_offset = self.center_new_window(new_window_width, new_window_height, self.root)
        self.add_pass_win.geometry(f"{new_window_width}x{new_window_height}+{x_offset}+{y_offset}")
        self.add_pass_win.resizable(False, False)
        self.add_pass_win.transient(self.root)        
        self.add_pass_win.lift()
        self.add_pass_win.focus_force()
        self.add_pass_win.after(250, lambda: self.add_pass_win.iconbitmap("static/padlock.ico"))             
        self.add_pass_win.grid_rowconfigure(0, weight=1)
        self.add_pass_win.grid_columnconfigure(0, weight=1)

        def submit_entry(event=None):
            name = name_entry.get()
            website = website_entry.get()
            username = username_entry.get()
            password = password_entry.get()
            comment = comment_entry.get()

            result = self.pwman.add_entry(name, username, password, website, comment)

            if result == "Entry successfully added.":
                self.root.unbind("<Return>")
                self.add_pass_win.destroy()
                self.add_pass_win.update()
                self.pass_frame_cache[name] = self.create_pass_tab_frame(name)                
                self.passwords_dash()
                self.selected_passwords_button(name)
            else:
                error_label.configure(text=result)

        self.add_pass_win.bind("<Return>", submit_entry)
        self.add_pass_win.bind("<Escape>", lambda event: self.add_pass_win.destroy())


        container_frame = ctk.CTkFrame(self.add_pass_win, fg_color="transparent")
        container_frame.grid(row=0, column=0, padx=25, pady=25, sticky="nsew")

        for i in range(8):
            container_frame.grid_rowconfigure(i, weight=1)
        container_frame.grid_columnconfigure(0, weight=1)
        container_frame.grid_columnconfigure(1, weight=1)

        name_label = ctk.CTkLabel(container_frame, text="* Name:", font=self.font_normal)
        name_label.grid(row=0, column=0, padx=5, pady=5)
        name_entry = ctk.CTkEntry(container_frame, font=self.font_entry)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.add_pass_win.after(100, lambda: name_entry.focus_set())        

        website_label = ctk.CTkLabel(container_frame, text="Website:", font=self.font_normal)
        website_label.grid(row=1, column=0, padx=5, pady=5)
        website_entry = ctk.CTkEntry(container_frame, font=self.font_entry)
        website_entry.grid(row=1, column=1, padx=5, pady=5)

        username_label = ctk.CTkLabel(container_frame, text="* Username:", font=self.font_normal)
        username_label.grid(row=2, column=0, padx=5, pady=5)
        username_entry = ctk.CTkEntry(container_frame, font=self.font_entry)
        username_entry.grid(row=2, column=1, padx=5, pady=5)        

        password_label = ctk.CTkLabel(container_frame, text="* Password:", font=self.font_normal)
        password_label.grid(row=3, column=0, padx=5, pady=5)
        password_entry = ctk.CTkEntry(container_frame, font=self.font_entry)
        password_entry.grid(row=3, column=1, padx=5, pady=5)

        comment_label = ctk.CTkLabel(container_frame, text="Comment:", font=self.font_normal)
        comment_label.grid(row=4, column=0, padx=5, pady=5)
        comment_entry = ctk.CTkEntry(container_frame, font=self.font_entry)
        comment_entry.grid(row=4, column=1, padx=5, pady=5)

        help_label = ctk.CTkLabel(container_frame, text='Fields with * are required', font=self.font_help)
        help_label.grid(row=5, column=0, padx=5, pady=10, columnspan=2)

        submit_button = ctk.CTkButton(container_frame, text="Submit", font=self.font_button, command=submit_entry)
        submit_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        error_label = ctk.CTkLabel(container_frame, text="", font=self.font_help)
        error_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    def delete_password(self):
        if self.selected_pass_name:
            confirm = CTkMessagebox(
                master=self.root,
                message=f'Are you sure you want to delete "{self.selected_pass_name}" entry?', 
                title="Confirm to delete this entry",
                icon="question",
                option_1="OK",
                option_2="Cancel"
            )

            response = confirm.get()
            if response == "OK":
                entries = self.db.execute_query("SELECT * FROM passwords WHERE name = ?", (self.selected_pass_name,))
                if entries:
                    for entry in entries:
                        self.pwman.delete_entry(entry["entry_id"])

                self.passwords_dash()
            else:
                pass
        else:
            pass

    def get_pass_tab(self, name):
        self.forget_frame_widgets(self.pass_right_frame_main)
        self.pass_right_frame_header_label.grid(row=0, column=0, padx=25, pady=5, sticky="w")
        self.pass_right_frame_header_label.configure(text=f"Passwords for {name}")

        self.pass_right_frame_header_separator = ctk.CTkFrame(self.pass_right_frame_header, height=self.width_separator, fg_color=self.bcolor_separator, corner_radius=self.corrad_separator)
        self.pass_right_frame_header_separator.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        if name not in self.pass_frame_cache:
            print(f"Creating new frame for {name}")
            self.pass_frame_cache[name] = self.create_pass_tab_frame(name)
        else:
            # Clear any help messages that might be in the cached frame
            self.clear_help_labels(self.pass_frame_cache[name])
        
        print(f"Getting passwords for {name} from cache")
        self.pass_frame_cache[name].grid(row=0, column=0, sticky="nsew")

    def create_pass_tab_frame(self, name):
        entries = self.pwman.get_entries(self.auth.current_user, name=name)
        button_width = 50
        original_values = {}        

        password_visibility = {}
        # Function to toggle password visibility
        def toggle_password(entry_widget, toggle_btn, entry_id):
            if password_visibility[entry_id]:  # If currently visible, hide it
                entry_widget.configure(show="*")  
                toggle_btn.configure(text="Show")
                password_visibility[entry_id] = False
            else:  # If currently hidden, show it
                entry_widget.configure(show="")  
                toggle_btn.configure(text="Hide")
                password_visibility[entry_id] = True

        # Function to open the website
        def open_website(entry_widget):
            url = entry_widget.get().strip()
            if url:
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url  # Ensure the URL is correctly formatted
                webbrowser.open(url)

        # Function to save field
        def save_field(old_text, field_name, entry_widget, entry_id, help_label):
            new_value = entry_widget.get()
            if old_text == new_value:
                return
            result = self.pwman.update_entry(entry_id, field_name, new_value)

            help_label.configure(text=result)

            if result in ("Name updated successfully.", 
                          "Username updated successfully.", 
                          "Website updated successfully.", 
                          "Comment updated successfully.", 
                          "Password updated successfully."):
                original_values[(entry_id, field_name)] = new_value
                entry_widget.configure(fg_color="#06402B")
                entry_widget.after(500, lambda: entry_widget.configure(fg_color="#343638"))
                pass
                if result == "Name updated successfully.":
                    self.update_cached_name(old_text)
                    self.update_cached_name(new_value)               
                    self.passwords_dash()
                    self.selected_passwords_button(new_value)
            else:
                entry_widget.configure(fg_color="#6B0402")
                entry_widget.after(500, lambda: entry_widget.configure(fg_color="#343638"))
                entry_widget.delete(0, ctk.END)
                entry_widget.insert(0, old_text)

        # Function to copy text
        def copy_to_clipboard(entry_widget, help_label):
            self.pass_right_frame_main.clipboard_clear()
            self.pass_right_frame_main.clipboard_append(entry_widget.get())
            self.pass_right_frame_main.update()
            help_label.configure(text=f"Copied to clipboard: {entry_widget.get()}")

        # Function to delete a specific entry
        def delete_entry(entry_id, frame, name):
            confirm = CTkMessagebox(
                master=self.root,
                message=f'Are you sure you want to delete this entry?', 
                title="Confirm to delete this entry",
                icon="question",
                option_1="OK",
                option_2="Cancel"
            )

            response = confirm.get()
            if response == "OK":
                self.pwman.delete_entry(entry_id)  # Remove from database
                frame.destroy()  # Remove the frame from UI
                self.passwords_dash()
                self.selected_passwords_button(name)
            else:
                pass

        # Handle focus out event to reset entries to original values
        def on_focus_out(event, entry_id, field_key):
            # If the field value is different from original and not yet saved
            current_value = event.widget.get()
            original_value = original_values.get((entry_id, field_key), "")
            
            if current_value != original_value:
                # Reset to original value
                event.widget.delete(0, "end")
                event.widget.insert(0, original_value)

        container = ctk.CTkScrollableFrame(self.pass_right_frame_main)
        container.grid_columnconfigure(0, weight=1)

        for i, entry in enumerate(entries):
            container.grid_rowconfigure(i, weight=1)
            pass_entry_frame = ctk.CTkFrame(container, fg_color="transparent")
            pass_entry_frame.grid(row=i, column=0, sticky="nsew", padx=5, pady=(5, 20))

            fields = [
                ("Name", "name"),
                ("Website", "website"),
                ("Username", "username"),
                ("Password", "password"),
                ("Comment", "comment"),
            ]

            help_label = ctk.CTkLabel(pass_entry_frame, text="", font=self.font_help_del)
            help_label.grid(row=len(fields), column=0, padx=5, pady=(5, 0), columnspan=5)

            for row, (label_text, field_key) in enumerate(fields):
                ctk.CTkLabel(pass_entry_frame, text=f"{label_text}: ", font=self.font_dash).grid(row=row, column=0, padx=5, pady=5)

                entry_widget = ctk.CTkEntry(pass_entry_frame, font=self.font_entry, width=200)
                
                # Store the original value
                field_value = entry[field_key] if entry[field_key] is not None else ""
                original_values[(entry["entry_id"], field_key)] = field_value
                
                entry_widget.insert(0, field_value)
                
                if field_key == "password":
                    entry_widget.configure(show="*")  
                    password_visibility[entry["entry_id"]] = False  

                # Bind the focus out event to reset the entry if needed
                entry_widget.bind("<FocusOut>", lambda e, eid=entry["entry_id"], fk=field_key: on_focus_out(e, eid, fk))

                entry_widget.grid(row=row, column=1, padx=5, pady=5)

                save_btn = ctk.CTkButton(pass_entry_frame, text="Save", width=button_width, 
                    command=lambda old=field_value, e=entry_widget, f=field_key, eid=entry["entry_id"], h=help_label: save_field(old, f, e, eid, h))
                save_btn.grid(row=row, column=2, padx=2, pady=5)

                copy_btn = ctk.CTkButton(pass_entry_frame, text="Copy", width=button_width, 
                    command=lambda e=entry_widget, h=help_label: copy_to_clipboard(e, h))
                copy_btn.grid(row=row, column=3, padx=2, pady=5)

                if field_key == "website":
                    go_btn = ctk.CTkButton(pass_entry_frame, text="Go", width=button_width, 
                        command=lambda e=entry_widget: open_website(e))
                    go_btn.grid(row=row, column=4, padx=2, pady=5)

                if field_key == "password":
                    toggle_btn = ctk.CTkButton(pass_entry_frame, text="Show", width=button_width)
                    toggle_btn.grid(row=row, column=4, padx=2, pady=5)                    
                    toggle_btn.configure(command=lambda e=entry_widget, btn=toggle_btn, eid=entry["entry_id"]: toggle_password(e, btn, eid))

            # Date info
            date_label = entry.get("date_modified") or entry.get("date_created")
            ctk.CTkLabel(pass_entry_frame, text=f"Last modified: {date_label}", font=self.font_help).grid(row=len(fields) + 1, column=0, padx=5, pady=5, columnspan=5)

            delete_btn = ctk.CTkButton(
                pass_entry_frame, text="Delete", fg_color="#BF573A", hover_color="#823232",
                command=lambda eid=entry["entry_id"], f=pass_entry_frame, n=entry["name"]: delete_entry(eid, f, n)
            )
            delete_btn.grid(row=len(fields) + 2, column=0, padx=5, pady=5, columnspan=5)

            separator_bottom = ctk.CTkFrame(pass_entry_frame, height=self.width_separator, fg_color=self.bcolor_separator, corner_radius=self.corrad_separator)
            separator_bottom.grid(row=len(fields) + 3, column=0, columnspan=5, sticky="ew", padx=5, pady=5)

        return container


    def get_user_passwords(self, user_id):
        passwords = self.db.execute_query("SELECT * FROM passwords WHERE user_id = ?", (user_id,))
        return passwords
    
    def get_password_names(self, passwords = None):
        if passwords is None:
            passwords = self.get_user_passwords(self.auth.current_user)
        # Extract unique names from the list of passwords
        return list({password["name"] for password in passwords})
    
    def cache_all_passwords(self):
        names = self.get_password_names()
        for name in names:
            self.pass_frame_cache[name] = self.create_pass_tab_frame(name)

    def update_cached_name(self, name):
        """ Update the name of a cached password frame """
        if name in self.pass_frame_cache:
            self.pass_frame_cache[name] = self.create_pass_tab_frame(name)

    def populate_password_buttons(self, order = None):
        """ Populates password buttons inside the frame dynamically. """       
        self.clear_frame(self.pass_left_frame_main)

        self.user_passwords = self.get_user_passwords(self.auth.current_user)

        self.all_passwords_buttons = {}
        
        if order == "az":
            sorted_password_names = sorted(self.get_password_names(self.user_passwords), key=str.lower)
        elif order == "za":
            sorted_password_names = sorted(self.get_password_names(self.user_passwords), key=str.lower, reverse=True)
        else:
            sorted_password_names = sorted(self.get_password_names(self.user_passwords), key=str.lower)

        for i, name in enumerate(sorted_password_names):
            pass_names_btn = ctk.CTkButton(
                self.pass_left_frame_main, 
                text=name, 
                command=lambda n=name: self.selected_passwords_button(n), 
                font=self.font_pass_name,                                                  
                height=40,
                corner_radius=self.corrad_pass_name,
                fg_color=self.color_pass_name,
                hover_color=self.color_pass_name_hover,
                border_color=self.bcolor_pass_name,            
            )
            pass_names_btn.grid(row=i, column=0, sticky="ew", padx=5, pady=1)
            self.all_passwords_buttons[name] = pass_names_btn  

    def invalidate_frame(self, name):
        if name in self.pass_frame_cache:
            del self.pass_frame_cache[name]

    def filter_password_buttons(self, event=None):
        """Filters password buttons based on search text, showing only those that start with the search text."""
        search_text = self.pass_left_frame_search.get().lower()
        
        # If search is empty, show all buttons
        if not search_text:
            for name, button in self.all_passwords_buttons.items():
                button.grid()
            return
        
        # Filter buttons based on search text
        for name, button in self.all_passwords_buttons.items():
            if name.lower().startswith(search_text):
                # Show button if it starts with the search text
                button.grid()
            else:
                # Hide button if it doesn't start with the search text
                button.grid_remove()

    def clear_help_labels(self, frame):
        """Clear text from all help labels in the given frame"""
        # Find all help labels within the frame and its children
        for widget in frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                # If it's a frame, recursively search its children
                self.clear_help_labels(widget)
            elif isinstance(widget, ctk.CTkLabel) and widget.cget("font") == self.font_help_del:
                # If it's a help label (identified by font), clear it
                widget.configure(text="")

###### <<<<<<<<<<<<<<<<<<<< Password Generator >>>>>>>>>>>>>>>>>>>> #####

    def pass_gen_dash(self):
        self.root.title(f"Password Manager - Dashboard - User: {self.user['username']} - Password Generator")

        self.passgen_container_frame.tkraise()

    def fill_pass_gen_frame(self):

        width = 100

        self.passgen_header_frame = ctk.CTkFrame(self.passgen_container_frame, fg_color="transparent")
        self.passgen_header_frame.grid(row=0, column=0, padx=20, pady=30, sticky="new")
        self.passgen_header_frame.grid_columnconfigure(0, weight=1)

        self.passgen_main_frame = ctk.CTkFrame(self.passgen_container_frame, fg_color="transparent")
        self.passgen_main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.passgen_main_frame.columnconfigure(2, weight=1)

        self.passgen_title = ctk.CTkLabel(self.passgen_header_frame, text="Password Generator", font=self.font_title, anchor="w")
        self.passgen_title.grid(row=0, column=0, padx=25, pady=5, sticky="w")

        self.passgen_header_separator = ctk.CTkFrame(self.passgen_header_frame, height=self.width_separator, fg_color=self.bcolor_separator, corner_radius=self.corrad_separator)
        self.passgen_header_separator.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.passgen_length_label = ctk.CTkLabel(self.passgen_main_frame, text="Length of password:", font=self.font_normal)
        self.passgen_length_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.passgen_length_entry = ctk.CTkEntry(self.passgen_main_frame, font=self.font_entry, width=width)
        self.passgen_length_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.passgen_length_entry.insert(0, "12")

        self.passgen_digits_label = ctk.CTkLabel(self.passgen_main_frame, text="How many digits:", font=self.font_normal)
        self.passgen_digits_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.passgen_digits_entry = ctk.CTkEntry(self.passgen_main_frame, font=self.font_entry, width=width)
        self.passgen_digits_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.passgen_digits_entry.insert(0, "2")

        self.passgen_symbols_label = ctk.CTkLabel(self.passgen_main_frame, text="How many special symbols (@, !, etc.):", font=self.font_normal)
        self.passgen_symbols_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.passgen_symbols_entry = ctk.CTkEntry(self.passgen_main_frame, font=self.font_entry, width=width)
        self.passgen_symbols_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.passgen_symbols_entry.insert(0, "2")

        self.passgen_word_label = ctk.CTkLabel(self.passgen_main_frame, text="Include word (e.g. 'john'):", font=self.font_normal)
        self.passgen_word_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.passgen_word_entry = ctk.CTkEntry(self.passgen_main_frame, font=self.font_entry, width=width)
        self.passgen_word_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.passgen_uppercase_checkbox = ctk.CTkCheckBox(self.passgen_main_frame, text="Include uppercase letters", font=self.font_normal)
        self.passgen_uppercase_checkbox.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.passgen_uppercase_checkbox.select()

        self.passgen_generate_button = ctk.CTkButton(self.passgen_main_frame, text="Generate", font=self.font_std_button, command=self.generate_password)
        self.passgen_generate_button.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        
        self.passgen_result_help = ctk.CTkLabel(self.passgen_main_frame, text="", font=self.font_help)
        self.passgen_result_help.grid(row=6, column=0, padx=5, pady=5, sticky="w")

        self.passgen_result_label = ctk.CTkLabel(self.passgen_main_frame, text="Generated password:", font=self.font_normal)
        self.passgen_result_label.grid(row=1, column=2, padx=5, pady=5)

        self.passgen_result_entry = ctk.CTkEntry(self.passgen_main_frame, font=self.font_entry, width=200)
        self.passgen_result_entry.grid(row=2, column=2, padx=5, pady=5)

        self.passgen_result_copybtn = ctk.CTkButton(self.passgen_main_frame, text="Copy", font=self.font_std_button, command=self.copy_password)
        self.passgen_result_copybtn.grid(row=3, column=2, padx=5, pady=5)

    def generate_password(self):
        try:
            length = int(self.passgen_length_entry.get())
            digits = int(self.passgen_digits_entry.get())
            symbols = int(self.passgen_symbols_entry.get())
            word = self.passgen_word_entry.get()
        except ValueError:
            self.passgen_result_help.configure(text="Please enter valid numbers.")
            return

        if length < 1 or digits < 0 or symbols < 0 or (digits + symbols) > length:
            self.passgen_result_help.configure(text="Invalid input values.")
            return
        
        if len(word) > length:
            self.passgen_result_help.configure(text="Word length exceeds required password length.")
            return
        
        if length < (digits + symbols + len(word)):
            self.passgen_result_help.configure(text="Length of password is too short for given settings.")
            return

        uppercase = self.passgen_uppercase_checkbox.get()
        password = self.passgen.generate(length, digits, symbols, uppercase, word)

        self.passgen_result_entry.delete(0, ctk.END)
        self.passgen_result_entry.insert(0, password)
        self.passgen_result_help.configure(text="Password generated successfully.")

    def copy_password(self):
        password = self.passgen_result_entry.get()
        if password:
            self.passgen_main_frame.clipboard_clear()
            self.passgen_main_frame.clipboard_append(password)
            self.passgen_main_frame.update()
            self.passgen_result_help.configure(text=f"Copied to clipboard: {password}")
        else:
            self.passgen_result_help.configure(text="No password to copy.")
        self.passgen_result_help.after(2000, lambda: self.passgen_result_help.configure(text=""))

###### <<<<<<<<<<<<<<<<<<<< Import Data >>>>>>>>>>>>>>>>>>>> #####

    def import_data_dash(self):
        self.root.title(f"Password Manager - Dashboard - User: {self.user['username']} - Import Data")
         
        self.indata_container_frame.tkraise()

    def fill_import_data_frame(self):        

        self.indata_header_frame = ctk.CTkFrame(self.indata_container_frame, fg_color="transparent")
        self.indata_header_frame.grid(row=0, column=0, padx=20, pady=30, sticky="new")
        self.indata_header_frame.grid_columnconfigure(0, weight=1)

        self.indata_main_frame = ctk.CTkFrame(self.indata_container_frame, fg_color="transparent")
        self.indata_main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.indata_title_label = ctk.CTkLabel(self.indata_header_frame, text="Import Your Passwords", font=self.font_title, anchor="w")
        self.indata_title_label.grid(row=0, column=0, padx=25, pady=5, sticky="w")

        self.indata_header_separator = ctk.CTkFrame(self.indata_header_frame, height=self.width_separator, fg_color=self.bcolor_separator, corner_radius=self.corrad_separator)
        self.indata_header_separator.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.indata_select_label = ctk.CTkLabel(self.indata_main_frame, text="Select file:", font=self.font_normal)
        self.indata_select_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.indata_select_entry = ctk.CTkEntry(self.indata_main_frame, font=self.font_entry, width=300)
        self.indata_select_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.indata_select_button = ctk.CTkButton(self.indata_main_frame, text="Browse", font=self.font_std_button, width=1, command=self.browse_import_path)
        self.indata_select_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.indata_import_button = ctk.CTkButton(self.indata_main_frame, text="Import", font=self.font_std_button, command=self.import_data)
        self.indata_import_button.grid(row=1, column=0, padx=5, pady=(15, 5), sticky="w")

        self.indata_help_label = ctk.CTkLabel(self.indata_main_frame, text="", font=self.font_help)
        self.indata_help_label.grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky="w")

    def browse_import_path(self):
        """Open file dialog to select import path."""
        file_path = tk.filedialog.askopenfilename(
            title="Select Import Path",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.indata_select_entry.delete(0, ctk.END)
            self.indata_select_entry.insert(0, file_path)

    def import_data(self):
        """Import passwords from a CSV file."""
        import_path = self.indata_select_entry.get()

        if not import_path:
            self.indata_help_label.configure(text="Please select a file.")
            return

        try:
            df = pd.read_csv(import_path)
            if df.empty:
                self.indata_help_label.configure(text="The file is empty.")
                return            
            
            self.indata_help_label.configure(text="Importing... Please wait.")
            self.indata_help_label.update_idletasks()  # Force the label to update immediately

            imported_passwords = 0
            replicate_entries = 0

            for _, row in df.iterrows():
                name = row["name"]
                website = row["website"]
                username = row["username"]
                password = row["password"]
                comment = row["comment"]

                # Check if the entry already exists
                check_result = self.pwman.check_entry(name, username, password)

                # If no such entry exists, add it to the database
                if check_result == "Entry does not exist.":    
                    self.pwman.add_entry(name, username, password, website, comment)
                    imported_passwords += 1
                # If the entry already exists, skip it and add to the replicate count
                elif check_result == "Entry already exists.":                   
                    replicate_entries += 1

            if imported_passwords > 0:   
                self.pass_frame_cache.clear()  # Clear the password frame cache
                self.cache_all_passwords()  # Re-cache all passwords
                if replicate_entries > 0:
                    self.indata_help_label.configure(text=f"{imported_passwords} password(s) imported successfully. {replicate_entries} password(s) already exist.")
                else:
                    self.indata_help_label.configure(text=f"{imported_passwords} password(s) imported successfully.")
            else:
                self.indata_help_label.configure(text="No new passwords imported.")            

        except Exception as e:
            self.indata_help_label.configure(text=f"Failed to import passwords: {e}")

###### <<<<<<<<<<<<<<<<<<<< Export Data >>>>>>>>>>>>>>>>>>>> #####

    def export_data_dash(self):
        self.root.title(f"Password Manager - Dashboard - User: {self.user['username']} - Export Data")

        self.outdata_container_frame.tkraise()

    def fill_export_data_frame(self):

        self.outdata_header_frame = ctk.CTkFrame(self.outdata_container_frame, fg_color="transparent")
        self.outdata_header_frame.grid(row=0, column=0, padx=20, pady=30, sticky="new")
        self.outdata_header_frame.grid_columnconfigure(0, weight=1)

        self.outdata_main_frame = ctk.CTkFrame(self.outdata_container_frame, fg_color="transparent")
        self.outdata_main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.outdata_title = ctk.CTkLabel(self.outdata_header_frame, text="Export Your Passwords", font=self.font_title, anchor="w")    
        self.outdata_title.grid(row=0, column=0, padx=25, pady=5, sticky="w")

        self.outdata_header_separator = ctk.CTkFrame(self.outdata_header_frame, height=self.width_separator, fg_color=self.bcolor_separator, corner_radius=self.corrad_separator)
        self.outdata_header_separator.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.outdata_select_label = ctk.CTkLabel(self.outdata_main_frame, text="Select destination:", font=self.font_normal)
        self.outdata_select_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.outdata_select_entry = ctk.CTkEntry(self.outdata_main_frame, font=self.font_entry, width=300)
        self.outdata_select_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.outdata_select_button = ctk.CTkButton(self.outdata_main_frame, text="Browse", font=self.font_std_button, width=1, command=self.browse_export_path)
        self.outdata_select_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.outdata_export_button = ctk.CTkButton(self.outdata_main_frame, text="Export", font=self.font_std_button, command=self.export_data)
        self.outdata_export_button.grid(row=1, column=0, padx=5, pady=(15, 5), sticky="w")

        self.outdata_help_label = ctk.CTkLabel(self.outdata_main_frame, text="", font=self.font_help)
        self.outdata_help_label.grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky="w")

    def export_data(self):
        """Export passwords to a CSV file."""
        export_path = self.outdata_select_entry.get()

        if not export_path:
            self.outdata_help_label.configure(text="Please select a destination path.")
            return

        # Get all passwords for the current user
        passwords = self.pwman.get_entries(self.auth.current_user)

        edited_passwords = []
        for password in passwords:
            password_dict = {
                "name": password["name"],
                "website": password["website"],
                "username": password["username"],
                "password": password["password"],
                "comment": password["comment"],
            }
            edited_passwords.append(password_dict)

        # Create a DataFrame from the passwords
        df = pd.DataFrame(edited_passwords)

        # Export to CSV
        try:
            df.to_csv(export_path, index=False)
            self.outdata_help_label.configure(text="Passwords exported successfully.")
        except Exception as e:
            self.outdata_help_label.configure(text=f"Failed to export passwords: {e}")
    
    def browse_export_path(self):
        """Open file dialog to select export path."""
        file_path = tk.filedialog.asksaveasfilename(
            title="Select Export Path",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.outdata_select_entry.delete(0, ctk.END)
            self.outdata_select_entry.insert(0, file_path)

###### <<<<<<<<<<<<<<<<<<<< Statistics >>>>>>>>>>>>>>>>>>>> #####

    def statistics_dash(self):
        self.root.title(f"Password Manager - Dashboard - User: {self.user['username']} - Statistics")

        self.stats_container_frame.tkraise()

    def fill_statistics_frame(self):

        self.stats_header_frame = ctk.CTkFrame(self.stats_container_frame, fg_color="transparent")
        self.stats_header_frame.grid(row=0, column=0, padx=20, pady=30, sticky="new")
        self.stats_header_frame.grid_columnconfigure(0, weight=1)

        self.stats_main_frame = ctk.CTkFrame(self.stats_container_frame, fg_color="transparent")
        self.stats_main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.stats_title = ctk.CTkLabel(self.stats_header_frame, text="Statistics", font=self.font_title, anchor="w")
        self.stats_title.grid(row=0, column=0, padx=25, pady=5, sticky="w")

        self.stats_header_separator = ctk.CTkFrame(self.stats_header_frame, height=self.width_separator, fg_color=self.bcolor_separator, corner_radius=self.corrad_separator)
        self.stats_header_separator.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.stats_totalpass_label = ctk.CTkLabel(self.stats_main_frame, text="Total passwords:", font=self.font_normal)
        self.stats_totalpass_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.stats_totalpass_label2 = ctk.CTkLabel(self.stats_main_frame, text=str(len(self.get_user_passwords(self.user["user_id"]))), font=self.font_normal)
        self.stats_totalpass_label2.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.stats_popular_label = ctk.CTkLabel(self.stats_main_frame, text="Most popular password:", font=self.font_normal)
        self.stats_popular_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.stats_popular_label2 = ctk.CTkLabel(self.stats_main_frame, text=self.most_popular_password(), font=self.font_normal)
        self.stats_popular_label2.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    def most_popular_password(self):
        """Get the most popular password from the database."""
        entries = self.pwman.get_entries(self.user["user_id"])
        if not entries:
            return "No passwords found."
        
        password_counts = {}

        for password in entries:
            password_text = password["password"]
            if password_text in password_counts:
                password_counts[password_text] += 1
            else:
                password_counts[password_text] = 1

        # Find the most common password
        most_common_password = max(password_counts, key=password_counts.get)
        return most_common_password

###### <<<<<<<<<<<<<<<<<<<< User (Settings) >>>>>>>>>>>>>>>>>>>> #####

    def user_dash(self):
        self.root.title(f"Password Manager - Dashboard - User: {self.user['username']} - Settings")

        self.user_container_frame.tkraise()

    def fill_user_frame(self):
        self.user_header_frame = ctk.CTkFrame(self.user_container_frame, fg_color="transparent")
        self.user_header_frame.grid(row=0, column=0, padx=20, pady=30, sticky="new")
        self.user_header_frame.grid_columnconfigure(0, weight=1)

        self.user_main_frame = ctk.CTkFrame(self.user_container_frame, fg_color="transparent")
        self.user_main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.user_title = ctk.CTkLabel(self.user_header_frame, text="User Settings", font=self.font_title, anchor="w")
        self.user_title.grid(row=0, column=0, padx=25, pady=5, sticky="w")
       
        self.user_header_separator = ctk.CTkFrame(self.user_header_frame, height=self.width_separator, fg_color=self.bcolor_separator, corner_radius=self.corrad_separator)
        self.user_header_separator.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.user_username_label = ctk.CTkLabel(self.user_main_frame, text="Current username:", font=self.font_normal)
        self.user_username_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.user_username_label2 = ctk.CTkLabel(self.user_main_frame, text=self.user["username"], font=self.font_normal)
        self.user_username_label2.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.user_newusername_label = ctk.CTkLabel(self.user_main_frame, text="New username:", font=self.font_normal)
        self.user_newusername_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.user_newusername_entry = ctk.CTkEntry(self.user_main_frame, font=self.font_entry)
        self.user_newusername_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.user_newusername_button = ctk.CTkButton(self.user_main_frame, text="Change", font=self.font_std_button,
            command=lambda: self.update_username(username=self.user_newusername_entry.get()))
        self.user_newusername_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.user_newusername_help_label = ctk.CTkLabel(self.user_main_frame, text="", font=self.font_help)
        self.user_newusername_help_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.user_cuurentpass_label = ctk.CTkLabel(self.user_main_frame, text="Enter current password:", font=self.font_normal)
        self.user_cuurentpass_label.grid(row=4, column=0, padx=5, pady=(20, 5), sticky="w")

        self.user_currentpass_entry = ctk.CTkEntry(self.user_main_frame, font=self.font_entry, show="*")
        self.user_currentpass_entry.grid(row=4, column=1, padx=5, pady=(15, 5), sticky="w")

        self.user_newpass_label = ctk.CTkLabel(self.user_main_frame, text="Enter new password:", font=self.font_normal)
        self.user_newpass_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        self.user_newpass_entry = ctk.CTkEntry(self.user_main_frame, font=self.font_entry, show="*")
        self.user_newpass_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        self.user_renewpass_label = ctk.CTkLabel(self.user_main_frame, text="Re-enter new password:", font=self.font_normal)
        self.user_renewpass_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")

        self.user_renewpass_entry = ctk.CTkEntry(self.user_main_frame, font=self.font_entry, show="*")
        self.user_renewpass_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        self.user_newpass_button = ctk.CTkButton(self.user_main_frame, text="Change", font=self.font_std_button,
            command=lambda: self.update_password(current_password=self.user_currentpass_entry.get(), 
                                                 password=self.user_newpass_entry.get(), 
                                                 repassword=self.user_renewpass_entry.get()))
        self.user_newpass_button.grid(row=7, column=0, padx=5, pady=5, sticky="w")

        self.user_newpass_help_label = ctk.CTkLabel(self.user_main_frame, text="", font=self.font_help)
        self.user_newpass_help_label.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    def update_username(self, username):
        if not username:
            self.user_newusername_help_label.configure(text="Username cannot be empty.")
            return
        
        confirm = CTkMessagebox(
            master=self.root,
            message=f'Are you sure you want to change username?', 
            title="Confirm to change username",
            icon="question",
            option_1="OK",
            option_2="Cancel"
        )

        response = confirm.get()

        if response == "OK":
            result = self.auth.change_username(username)
            self.user_newusername_help_label.configure(text=result)

            if result == "Username changed successfully.":
                self.user_username_label2.configure(text=username)

    def update_password(self, current_password, password, repassword):
        if not current_password or not password or not repassword:
            self.user_newpass_help_label.configure(text="All fields are required.")
            return

        if password != repassword:
            self.user_newpass_help_label.configure(text="Passwords do not match.")
            return
        
        if current_password != self.pwman.user_password:
            self.user_newpass_help_label.configure(text="Current password is incorrect.")
            return

        confirm = CTkMessagebox(
            master=self.root,
            message=f'Are you sure you want to change password?', 
            title="Confirm to change password",
            icon="question",
            option_1="OK",
            option_2="Cancel"
        )

        response = confirm.get()

        if response == "OK":
            result = self.auth.change_password(current_password, password)
            self.user_newpass_help_label.configure(text=result)

###### <<<<<<<<<<<<<<<<<<<< Logout >>>>>>>>>>>>>>>>>>>> #####

    def logout(self):      
        confirm = CTkMessagebox(
            master=self.root,
            message=f'Are you sure you want to logout?', 
            title="Confirm to logout",
            icon="question",
            option_1="OK",
            option_2="Cancel"
        )

        response = confirm.get()

        if response == "OK":

            del self.auth
            del self.db
            del self.pwman

            gc.collect()

            self.auth = AuthManager()
            self.db = DatabaseManager()
            self.passgen = PasswordGenerator()
            self.pwman = None
            
            self.main_container.destroy()

            self.root.minsize(400, 300)
            self.center_window(400, 300)
            self.root.resizable(False, False)

            # Show login frame
            self.show_login_frame() 

        else:
            pass   

###### <<<<<<<<<<<<<<<<<<<< Helpers >>>>>>>>>>>>>>>>>>>> #####
    
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()  # Destroy all widgets in the frame

    def forget_frame_widgets(self, frame):
        for widget in frame.winfo_children():
            widget.grid_forget()

    def center_window(self, width=300, height=300):
        if self.root.state() == "zoomed":
            self.root.state("normal")
        self.root.update_idletasks()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def center_new_window(self, x, y, root_window):
        """ 
        Takes size of new window and the name of root window as arguments. 
        Returns (x_offset, y_offset) to center the new window on the root window. 
        """
        # Get root window position and size
        root_window.update_idletasks() # Ensure dimensions are updated
        root_x = root_window.winfo_x()
        root_y = root_window.winfo_y()
        root_width = root_window.winfo_width()
        root_height = root_window.winfo_height()

        # Calculate position to center the new window on the main window
        x_offset = root_x + (root_width // 2) - (x // 2)
        y_offset = root_y + (root_height // 2) - (y // 2)

        return x_offset, y_offset


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    gui = PasswordManagerGUI(root)
    root.mainloop()
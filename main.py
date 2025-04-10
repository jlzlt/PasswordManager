import customtkinter as ctk
from gui import PasswordManagerGUI


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    gui = PasswordManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

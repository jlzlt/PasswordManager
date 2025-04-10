# PasswordManager

A secure and minimalistic password manager application that allows users to store, retrieve, and manage their sensitive credentials locally. The application uses strong encryption to protect stored passwords and provides an easy-to-use interface for adding, updating, and deleting entries.

All data is encrypted using a master password, which is never stored anywhere. Without the correct master password, data cannot be decrypted.

## Installation Guide

Follow these steps to set up and run PasswordManager on your local machine:

### 1.) Prerequisites
Make sure you have the following installed:

• Python 3.10+ (https://www.python.org/downloads/)  
• pip (comes with Python)  
• Git (https://git-scm.com/downloads)  
• Virtual Environment (venv) (optional but recommended)

### 2.) Clone the Repository
Open a terminal and run:  

`git clone https://github.com/jlzlt/PasswordManager.git`  
`cd PasswordManager`

### 3.) Create a Virtual Environment (Optional, Recommended)
To keep dependencies isolated, create and activate a virtual environment:

Windows:  
`python -m venv venv`  
`venv\Scripts\activate`  

Mac/Linux:  
`python3 -m venv venv`  
`source venv/bin/activate`  

### 4.) Install Dependencies
Install required Python packages:

`pip install -r requirements.txt`

### 5.) Run the Application
Start the application with:

`python main.py`

## Features

### Security & Encryption
PasswordManager uses a layered encryption model designed to maximize security while allowing for safe storage and retrieval of sensitive data.

- The password user registers with (master password) is stored in database hashed (thus safely unreadable)
- When a user registers their master password is combined with a unique user-specific salt (generated on registration) to create original encryption key
- This encryption key is then used to encrypt any passwords user stores
- Master password required to access any password data
- Data file is encrypted and unreadable without correct credentials

### Password Management

- Add new credentials (website, username, password, comment)
- View stored credentials (after decryption)
- Update existing credentials
- Delete credentials securely

### Extra Features

- Import and Export passwords in csv format
- Statistics of your passwords
- Generate a random password with some control

## Tech Stack

Python, CustomTkinter

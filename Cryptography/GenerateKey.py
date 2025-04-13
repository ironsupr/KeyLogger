from cryptography.fernet import Fernet
import os

def generate_key():
    key = Fernet.generate_key()
    key_path = os.path.join(os.path.dirname(__file__), 'encryption_key.key')
    with open(key_path, 'wb') as key_file:
        key_file.write(key)
    print(f"Key generated and saved to {key_path}")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    generate_key()

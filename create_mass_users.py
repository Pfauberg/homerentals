import requests
import random

API_URL = "http://127.0.0.1:8000/api/register/"

FIRST_NAMES = [
    "John", "Anna", "Max", "Linda", "David", "Sara", "Nick", "Olga", "Viktor", "Sophie",
    "Liam", "Emily", "Chris", "Nina", "Leon", "Elena", "Paul", "Mila", "Ivan", "Emma"
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson",
    "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Lee", "Walker"
]

ROLES = ['landlord'] * 5 + ['user'] * 25
random.shuffle(ROLES)

def generate_user(idx, role):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    username = f"{role}_api_{idx}_{random.randint(1000,9999)}"
    email = f"{first.lower()}.{last.lower()}.{random.randint(1000,9999)}@example.com"
    return {
        "username": username,
        "password": "password",
        "password2": "password",
        "first_name": first,
        "last_name": last,
        "email": email,
        "role": role
    }

def main():
    created = 0
    for idx, role in enumerate(ROLES, start=1):
        user_data = generate_user(idx, role)
        response = requests.post(API_URL, json=user_data)
        if response.status_code == 201:
            print(f"[+] Registered: {user_data['username']} ({user_data['role']}) | {user_data['email']}")
            created += 1
        else:
            print(f"[!] Error for {user_data['username']}: {response.status_code} {response.text}")

    print(f"\nDONE: {created} users created successfully.")

if __name__ == "__main__":
    main()

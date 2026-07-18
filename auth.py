"""
auth.py
Minimal role-based access control for SchoolMind AI.

This is intentionally simple (hardcoded users, plaintext password check)
to demonstrate role-aware design for a portfolio project. For anything
beyond a demo, passwords should be hashed (e.g. bcrypt) and users should
live in the database, not in source code.

Parent accounts: username = student's name (lowercase), password = "<Student Name>123"
"""

USERS = {
    "principal": {
        "password": "principal123",
        "role": "Principal",
    },
    "teacher": {
        "password": "teacher123",
        "role": "Teacher",
    },
    "aarav sharma": {"password": "Aarav Sharma123", "role": "Parent", "student_name": "Aarav Sharma"},
    "vihaan gupta": {"password": "Vihaan Gupta123", "role": "Parent", "student_name": "Vihaan Gupta"},
    "arjun kumar": {"password": "Arjun Kumar123", "role": "Parent", "student_name": "Arjun Kumar"},
    "aditya singh": {"password": "Aditya Singh123", "role": "Parent", "student_name": "Aditya Singh"},
    "krishna patel": {"password": "Krishna Patel123", "role": "Parent", "student_name": "Krishna Patel"},
    "rohan verma": {"password": "Rohan Verma123", "role": "Parent", "student_name": "Rohan Verma"},
    "ishaan nair": {"password": "Ishaan Nair123", "role": "Parent", "student_name": "Ishaan Nair"},
    "siddharth reddy": {"password": "Siddharth Reddy123", "role": "Parent", "student_name": "Siddharth Reddy"},
    "karthik rao": {"password": "Karthik Rao123", "role": "Parent", "student_name": "Karthik Rao"},
    "yash mehta": {"password": "Yash Mehta123", "role": "Parent", "student_name": "Yash Mehta"},
    "priya sharma": {"password": "Priya Sharma123", "role": "Parent", "student_name": "Priya Sharma"},
    "sneha gupta": {"password": "Sneha Gupta123", "role": "Parent", "student_name": "Sneha Gupta"},
    "ananya kumar": {"password": "Ananya Kumar123", "role": "Parent", "student_name": "Ananya Kumar"},
    "kavya singh": {"password": "Kavya Singh123", "role": "Parent", "student_name": "Kavya Singh"},
    "diya patel": {"password": "Diya Patel123", "role": "Parent", "student_name": "Diya Patel"},
    "aditi verma": {"password": "Aditi Verma123", "role": "Parent", "student_name": "Aditi Verma"},
    "meera nair": {"password": "Meera Nair123", "role": "Parent", "student_name": "Meera Nair"},
    "riya reddy": {"password": "Riya Reddy123", "role": "Parent", "student_name": "Riya Reddy"},
    "sanjana rao": {"password": "Sanjana Rao123", "role": "Parent", "student_name": "Sanjana Rao"},
    "pooja mehta": {"password": "Pooja Mehta123", "role": "Parent", "student_name": "Pooja Mehta"},
    "rahul sharma": {"password": "Rahul Sharma123", "role": "Parent", "student_name": "Rahul Sharma"},
    "aman gupta": {"password": "Aman Gupta123", "role": "Parent", "student_name": "Aman Gupta"},
    "nikhil kumar": {"password": "Nikhil Kumar123", "role": "Parent", "student_name": "Nikhil Kumar"},
    "rajat singh": {"password": "Rajat Singh123", "role": "Parent", "student_name": "Rajat Singh"},
    "harsh patel": {"password": "Harsh Patel123", "role": "Parent", "student_name": "Harsh Patel"},
    "manav verma": {"password": "Manav Verma123", "role": "Parent", "student_name": "Manav Verma"},
    "akash nair": {"password": "Akash Nair123", "role": "Parent", "student_name": "Akash Nair"},
    "vivek reddy": {"password": "Vivek Reddy123", "role": "Parent", "student_name": "Vivek Reddy"},
    "deepak rao": {"password": "Deepak Rao123", "role": "Parent", "student_name": "Deepak Rao"},
    "varun mehta": {"password": "Varun Mehta123", "role": "Parent", "student_name": "Varun Mehta"},
    "neha sharma": {"password": "Neha Sharma123", "role": "Parent", "student_name": "Neha Sharma"},
    "shreya gupta": {"password": "Shreya Gupta123", "role": "Parent", "student_name": "Shreya Gupta"},
    "ishita kumar": {"password": "Ishita Kumar123", "role": "Parent", "student_name": "Ishita Kumar"},
    "tanya singh": {"password": "Tanya Singh123", "role": "Parent", "student_name": "Tanya Singh"},
    "nandini patel": {"password": "Nandini Patel123", "role": "Parent", "student_name": "Nandini Patel"},
    "ritika verma": {"password": "Ritika Verma123", "role": "Parent", "student_name": "Ritika Verma"},
    "khushi nair": {"password": "Khushi Nair123", "role": "Parent", "student_name": "Khushi Nair"},
    "simran reddy": {"password": "Simran Reddy123", "role": "Parent", "student_name": "Simran Reddy"},
    "payal rao": {"password": "Payal Rao123", "role": "Parent", "student_name": "Payal Rao"},
    "muskan mehta": {"password": "Muskan Mehta123", "role": "Parent", "student_name": "Muskan Mehta"},
    "gautam sharma": {"password": "Gautam Sharma123", "role": "Parent", "student_name": "Gautam Sharma"},
    "abhishek gupta": {"password": "Abhishek Gupta123", "role": "Parent", "student_name": "Abhishek Gupta"},
    "pranav kumar": {"password": "Pranav Kumar123", "role": "Parent", "student_name": "Pranav Kumar"},
    "rishi singh": {"password": "Rishi Singh123", "role": "Parent", "student_name": "Rishi Singh"},
    "mohit patel": {"password": "Mohit Patel123", "role": "Parent", "student_name": "Mohit Patel"},
    "saurabh verma": {"password": "Saurabh Verma123", "role": "Parent", "student_name": "Saurabh Verma"},
    "rudra nair": {"password": "Rudra Nair123", "role": "Parent", "student_name": "Rudra Nair"},
    "chirag reddy": {"password": "Chirag Reddy123", "role": "Parent", "student_name": "Chirag Reddy"},
    "ayush rao": {"password": "Ayush Rao123", "role": "Parent", "student_name": "Ayush Rao"},
    "kunal mehta": {"password": "Kunal Mehta123", "role": "Parent", "student_name": "Kunal Mehta"},
}


def check_login(username, password):
    """Return the matching user's info dict if credentials are correct, else None."""
    user = USERS.get(username.lower().strip())
    if user and user["password"] == password:
        return user
    return None
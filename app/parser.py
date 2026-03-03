import re

def extract_email(text):
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return re.findall(pattern, text)

def extract_phone(text):
    pattern = r"(\+33|0)[1-9](\d{8})"
    return re.findall(pattern, text)
import random
import string

def generate_dummy_email():
    domains = ["example.com", "test.com", "dummy.com"]
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
    domain = random.choice(domains)
    return f"{username}@{domain}"

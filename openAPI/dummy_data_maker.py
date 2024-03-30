import random
import string
from datetime import datetime

def generate_dummy_email():
    domains = ["example.com", "test.com", "dummy.com"]
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
    domain = random.choice(domains)
    return f"{username}@{domain}"

def preprocessing_book_index(book_index):
    dummy_book_indx = "<p>Dummy Book Index<br>1.example index<br>2.example index<br>3.example index</p>"
    if not book_index.strip():
        return dummy_book_indx

    return book_index.replace("\r\n", "")

def generate_book_discount():
    values = [0, 10, 20]
    weights = [5, 3, 2]  # 각 값에 대한 가중치, 50%, 30%, 20%의 비율
    return random.choices(values, weights=weights)[0]

def generate_book_package():
    values = [0, 1]
    weights = [3, 7]  # 각 값에 대한 가중치, 30%, 70%의 비율
    return random.choices(values, weights=weights)[0]

def preprocessing_book_published(date):

    date_object = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %Z')

    return date_object.strftime('%Y-%m-%d')

def generate_book_stock():
    values = [200, 300]
    weights = [5, 5]  # 각 값에 대한 가중치, 30%, 70%의 비율
    return random.choices(values, weights=weights)[0]

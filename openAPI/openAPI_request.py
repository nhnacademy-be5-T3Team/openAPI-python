import requests
from bs4 import BeautifulSoup
import secret
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def openAPI_request_search(query, category_id):
    """알라딘 opan API 도서 검색 요청"""

    params = {
        'ttbkey': secret.aladin_open_api_ttbkey,
        'SearchTarget': 'Book',
        'MaxResults': '100',
        'Query': query,
        'CategoryId': category_id
    }

    response = requests.get(secret.aladin_open_api_search_url, params=params)

    if response.status_code == 200:

        content = response.text
        soup = BeautifulSoup(content, 'xml')
        data = soup.find_all("item")

        isbn_list = []
        if data:
            for item in data:
                if item.find("categoryId").get_text() == str(category_id):
                    if item.find("isbn13").get_text():
                        isbn_list.append(item.find("isbn13").get_text())

        return isbn_list

    else:
        # 응답이 실패한 경우
        print('Error:', response.status_code)


def remove_image_tags(text):
    """문자열에서 <img> 태그와 주변 문자열 제거"""
    return re.sub(r'<img[^>]+>', '', text)


def openAPI_request_detail(isbn_id):
    """알라딘 openAPI 도서 상세 요청"""

    params = {
        'ttbkey': secret.aladin_open_api_ttbkey,
        'itemIdType': 'ISBN13',
        'ItemId': isbn_id,
        'Cover': 'Big'
    }

    response = requests.get(secret.aladin_open_api_detail_url, params=params)

    if response.status_code == 200:

        content = response.text
        soup = BeautifulSoup(content, 'xml')
        data = soup.find("item")

        book_info = {}

        # 출판사
        publisher = data.find("publisher").get_text()
        if not publisher:
            publisher = "DefaultPublisherName"

        # 책 이름
        book_info["book_name"] = data.find("title").get_text()
        if not book_info["book_name"]:
            book_info["book_name"] = "DefaultBookName"

        # 책 목차
        book_info["book_index"] = data.find("bookinfo").find("toc").get_text()
        if not book_info["book_index"]:
            book_info["book_index"] = "DefaultBookIndex"

        # 책 설명
        book_info["book_desc"] = remove_image_tags(data.find("description").get_text())
        if not book_info["book_desc"]:
            book_info["book_desc"] = "DefaultBookDescription"

        # 책 ISBN-13
        book_info["book_isbn_13"] = data.find("isbn13").get_text()
        if not book_info["book_isbn_13"]:
            book_info["book_isbn_13"] = "DefaultBookIsbn13"

        # 책 가격
        book_info["book_price"] = data.find("priceStandard").get_text()
        if not book_info["book_price"]:
            book_info["book_price"] = "10000"

        # 출판일
        book_info["book_published"] = data.find("pubDate").get_text()
        if not book_info["book_published"]:
            book_info["book_published"] = "2024-01-01"

        # 책 커버 이미지 URL
        book_thumbnail_image_url = data.find("cover").get_text()

        # 책 미리보기 이미지 URL들
        book_image_list = [img.get_text() for img in data.find("bookinfo").find_all("letslookimg")]
        if not book_image_list:
            book_image_list = ["no-image"]

        # 작가들
        author_list = []
        for author in data.find("bookinfo").find("authors").find_all("author"):
            authorType = author.get("authorType")
            desc = author.get("desc")
            name = author.get_text()

            if not authorType:
                authorType = "DefaultAuthorType"
            if not desc:
                desc = "DefaultAuthorDesc"
            if not name:
                name = "DefaultAuthorName"

            author_info = {"authorType": authorType, "desc": desc, "name": name}
            author_list.append(author_info)

        # 파싱된 값들을 반환
        return {
            'publisher': publisher,
            'book_info': book_info,
            'book_thumbnail_image_url': book_thumbnail_image_url,
            'book_image_list': book_image_list,
            'author_list': author_list
        }

import requests
from bs4 import BeautifulSoup
import secret

def openAPI_request_search(query, category_id):
    # 쿼리 파라미터 변수로 담기
    params = {
        'ttbkey': secret.aladin_open_api_ttbkey,
        'SearchTarget':'Book',
        'MaxResults': '10',
        'Query': query,
        'CategoryId': category_id
    }

    # 요청을 보낼 URL
    url = secret.aladin_open_api_search_url

    # GET 요청을 보냄
    response = requests.get(url, params=params)

    # 응답 확인
    if response.status_code == 200:
        # xml 내용
        content = response.text
        soup = BeautifulSoup(content, 'xml')

        data = soup.find_all("item")

        isbn_list = []
        if data:
            for item in data:
                if(item.find("categoryId").get_text() == str(category_id)):
                    if item.find("isbn13").get_text():
                        isbn_list.append(item.find("isbn13").get_text())

        return isbn_list

    else:
        # 응답이 실패한 경우
        print('Error:', response.status_code)

def openAPI_request_detail(isbn_id):
    params = {
        'ttbkey': secret.aladin_open_api_ttbkey,
        'itemIdType' : 'ISBN13',
        'ItemId' : isbn_id
    }

    # 요청을 보낼 URL
    url = secret.aladin_open_api_detail_url

    # GET 요청을 보냄
    response = requests.get(url, params=params)

    # 응답 확인
    if response.status_code == 200:
        # xml 내용
        content = response.text
        soup = BeautifulSoup(content, 'xml')

        data = soup.find("item")

        # 출판사
        publisher = data.find("publisher").get_text()

        # 책 이름
        book_name = data.find("title").get_text()
        # 책 목차
        book_index = data.find("bookinfo").find("toc").get_text()
        # 책 설명
        book_desc = data.find("description").get_text()
        # 책 ISBN-13
        book_isbn_13 = data.find("isbn13").get_text()
        # 책 가격
        book_price = data.find("priceStandard").get_text()
        # 출판일
        book_published = data.find("pubDate").get_text()

        # 책 이미지 URL
        book_thumbnail_image_url = data.find("cover").get_text()

        # 책 이미지 URL들
        imgs = [img.get_text() for img in data.find("bookinfo").find_all("letslookimg")]

        # 작가들
        authors = [author.get_text() for author in data.find("bookinfo").find("authors").find_all("author")]

        # 파싱된 값들을 반환
        return {
            'publisher': publisher,
            'book_name': book_name,
            'book_index': book_index,
            'book_desc': book_desc,
            'book_isbn_13': book_isbn_13,
            'book_price': book_price,
            'book_published': book_published,
            'book_thumbnail_image_url': book_thumbnail_image_url,
            'imgs': imgs,
            'authors': authors
        }

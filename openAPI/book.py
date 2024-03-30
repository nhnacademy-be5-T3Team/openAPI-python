from mysql.insert_query import *
from openAPI_request import *
import pandas as pd


def isbn_list_by_category_id():
    list = []
    for index, row in df.iterrows():
        category_name = row['2Depth']
        category_id = row['CID_x']

        isbn_list = openAPI_request_search(category_name, category_id)

        if isbn_list:
            dict = {
                "category_name": category_name,
                "category_id": category_id,
                "isbn_list" : isbn_list
            }
            list.append(dict)
    return list

if __name__ == "__main__":
    # 테스트를 위해 잠시 주석 처리
    # csv_file_path = 'resources/mapped_child_category.csv'
    # df = pd.read_csv(csv_file_path)
    #
    # isbn_list = isbn_list_by_category_id()

    isbn_list = [{'category_name': '가계부', 'category_id': 90452, 'isbn_list': ['8809984880002', '8809983390007', '8809479920732', '8809529015272', '8809529015258', '8809529015265', '9788960306257', '8809850420028', '8809637010237', '8809637010220']}, {'category_name': '건강요리', 'category_id': 53471, 'isbn_list': ['9791189529116', '9788984688803']}]

    for item in isbn_list:
        isbns = item['isbn_list']

        for isbn in isbns:
            result = openAPI_request_detail("8809529015258")
            print(result)
            # result 테스트 예제
            # {'publisher': '헤르몬하우스', 'book_name': '고대표 돈 버는 가계부', 'book_index': ' ', 'book_desc': "<img src='https://image.aladin.co.kr/product/33074/32/coveroff/k872937307_1.jpg'/> 고대표 돈 버는 가계부 - 고혜진 지음 <br/> 파산의 어려움에서 매일 정리한 가계부로 다시 일어설 수 있었던 것처럼 저자의 절약 관리 노하우와 돈을 가장 효율적으로 가치 있게 쓰는 방법을 이 가계부 다이어리로 독자들과 함께 나누고자 한다.", 'book_isbn_13': '8809984880002', 'book_price': '15000', 'book_published': 'Thu, 04 Jan 2024 15:00:00 GMT', 'book_thumbnail_image_url': 'https://image.aladin.co.kr/product/33074/32/coversum/k872937307_1.jpg', 'imgs': ['https://image.aladin.co.kr/product/space.gif', 'https://image.aladin.co.kr/product/space.gif'], 'authors': [{'authorType': 'author', 'desc': '지은이', 'name': '고혜진'}]}

            conn, cursor = getConnection()

            if conn and cursor:

                # 출판사 데이터 insert
                inserted_publisher_id = insert_publisher(cursor, result['publisher'])

                # TODO : 도서 데이터 insert
                inserted_book_id = insert_book_info(cursor, result['book_info'], inserted_publisher_id)

                # TODO : 도서 썸네일 이미지 insert
                insert_book_thumbnail(cursor, inserted_book_id, result['book_thumbnail_image_url'])

                # TODO : 도서 미리보기 이미지 insert

                # TODO : 도서 참여자 insert

                # TODO : 도서 참여자 역할 insert

                # TODO : 도서 참여자 관계 insert

                conn.commit()
                conn.close()
                print("MySQL 연결이 닫혔습니다.")

            break

        break
from mysql.insert_query import *
from openAPI_request import *
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def isbn_list_by_category_id(df):
    """주어진 카테고리 아이디로 도서 검색 OpenAPI를 요청하여 도서 ISBN 목록을 반환합니다"""
    list = []
    for index, row in df.iterrows():
        category_name = row['2Depth']
        category_id = row['CID_x']

        isbn_list = openAPI_request_search(category_name, category_id)

        random_values = random.sample(isbn_list, 2)

        if isbn_list:
            dict = {
                "category_name": category_name,
                "category_id": category_id,
                "isbn_list": random_values
            }
            list.append(dict)

    return list


if __name__ == "__main__":
    csv_file_path = 'resources/mapped_child_category.csv'
    df = pd.read_csv(csv_file_path)

    isbn_list = isbn_list_by_category_id(df)

    for item in isbn_list:
        isbns = item['isbn_list']

        for isbn in isbns:
            result = openAPI_request_detail(isbn)

            conn, cursor = get_connection()

            if conn and cursor:

                # publishers 테이블에 데이터 insert
                inserted_publisher_id = insert_publisher(cursor, result['publisher'])

                # books 테이블에 데이터 insert
                inserted_book_id = insert_book_info(cursor, result['book_info'], inserted_publisher_id)

                # book_thumbnails 테이블에 데이터 insert
                insert_book_thumbnail(cursor, inserted_book_id, result['book_thumbnail_image_url'])

                # book_images 테이블에 데이터 insert
                insert_book_image(cursor, inserted_book_id, result['book_image_list'])

                for author in result['author_list']:
                    # participants 테이블에 데이터 insert
                    inserted_participant_id = insert_participant(cursor, author['name'])
                    # participant_roles 테이블에 데이터 insert
                    inserted_participant_role_id = insert_participant_role(cursor, author['authorType'])
                    # participant_role_registration 테이블에 데이터 insert
                    insert_participant_role_registration(cursor, inserted_book_id, inserted_participant_id,
                                                         inserted_participant_role_id)

                insert_book_category(cursor, inserted_book_id, item['category_id'])

                conn.commit()
                conn.close()
                print("MySQL 연결이 닫혔습니다.")

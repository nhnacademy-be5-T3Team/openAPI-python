from mysql.insert_query import *
from openAPI.category_data_extractor import save_df_to_csv
from openAPI_request import *
from openAPI.image_processor import *
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def isbn_list_by_category_id(df):
    """주어진 카테고리 아이디로 도서 검색 OpenAPI를 요청하여 도서 ISBN 목록을 반환합니다"""
    result_list = []
    for index, row in df.iterrows():
        category_name = row['2Depth']
        category_id = row['CID_x']

        isbn_list = openAPI_request_search(category_name.split('/')[0], category_id)
        logger.info(f"카테고리 : '{category_name.split('/')[0]}'에 대한 도서 검색 api 요청")

        # if len(isbn_list) >= 5:
        #     random_isbn_list = random.sample(isbn_list, 5)
        # else:
        #     random_isbn_list = isbn_list

        if isbn_list:
            data = {
                "category_name": category_name,
                "category_id": row['db_child_category_id'],
                "isbn_list": isbn_list
            }
            result_list.append(data)

    result_df = pd.DataFrame(result_list)
    save_df_to_csv(result_df, "openAPI_isbn.csv")

    return result_list


def read_csv_to_list(file_path):
    """CSV 파일을 읽어 리스트 안의 딕셔너리 구조로 반환합니다."""
    result_list = []
    try:
        df = pd.read_csv(file_path)

        for index, row in df.iterrows():
            data = {
                "category_name": row['category_name'],
                "category_id": row['category_id'],
                "isbn_list": eval(row['isbn_list'])
            }
            result_list.append(data)

        return result_list

    except Exception as e:
        logger.info("CSV 파일을 읽는 중 오류가 발생했습니다: {}", e)
        return None


if __name__ == "__main__":
    csv_file_path = 'resources/mapped_child_category.csv'
    df = pd.read_csv(csv_file_path)

    isbn_list = read_csv_to_list("resources/openAPI_isbn.csv")

    conn, cursor = get_connection()

    try:
        for item in isbn_list:
            for isbn in item['isbn_list']:
                try:
                    result = openAPI_request_detail(isbn)

                    # publishers 테이블에 데이터 insert
                    inserted_publisher_id = insert_publisher(cursor, result['publisher'])
                    # books 테이블에 데이터 insert
                    inserted_book_id = insert_book_info(cursor, result['book_info'], inserted_publisher_id)
                    # book_thumbnails 테이블에 데이터 insert
                    thumbnail = download_image(result['book_thumbnail_image_url'], "book_covers", inserted_book_id)
                    insert_book_thumbnail(cursor, inserted_book_id, thumbnail)
                    # book_images 테이블에 데이터 insert
                    for img_url in result['book_image_list']:
                        # 이미지 url이 올바르지 않은 경우 랜덤으로 테스트 이미지 선택해 삽입
                        if img_url in ["https://image.aladin.co.kr/product/space.gif", "no-image"]:
                            book_image = save_random_image("book_images", inserted_book_id)
                        else:
                            book_image = download_image(img_url, "book_images", inserted_book_id)
                        insert_book_image(cursor, inserted_book_id, book_image)

                    for author in result['author_list']:
                        # participants 테이블에 데이터 insert
                        inserted_participant_id = insert_participant(cursor, author['name'])
                        # participant_role_registration 테이블에 데이터 insert
                        inserted_participant_role_id = insert_participant_role(cursor, author['authorType'], author['desc'])
                        # participant_role_registration 테이블에 데이터 insert
                        insert_participant_role_registration(cursor, inserted_book_id, inserted_participant_id,
                                                             inserted_participant_role_id)

                    insert_book_category(cursor, inserted_book_id, item['category_id'])

                    conn.commit()
                    logger.info("데이터 삽입이 완료되었습니다.")
                except Exception as e:
                    logger.info("에러 발생 : {}", e)
                    conn.rollback()  # 에러가 발생했을 때 롤백
    finally:
        if conn:
            conn.close()
            logger.info("MySQL 연결이 닫혔습니다.")

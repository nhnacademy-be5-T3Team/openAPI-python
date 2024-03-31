import secret
import pymysql
import logging
from openAPI.dummy_data_maker import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection():
    """데이터베이스에 연결하고 커서를 반환합니다."""
    conn = pymysql.connect(
        host=secret.host,
        user=secret.user,
        password=secret.password,
        db=secret.database)
    logger.info("MySQL 데이터베이스에 연결되었습니다.")
    return conn, conn.cursor()


def execute_query(cursor, query, data=None):
    """주어진 쿼리를 실행합니다."""
    if data:
        cursor.execute(query, data)
    else:
        cursor.execute(query)


def insert_parent_categories(cursor, category_df):
    """카테고리 데이터프레임의 각 행을 순회하며 categories 테이블에 최상위 계층 부모 카테고리 데이터를 insert하고 primary key 값을 dataframe으로 반환합니다."""
    for index, row in category_df.iterrows():
        category_name = row['1Depth']
        insert_query = "INSERT INTO categories (category_name) VALUES (%s)"
        execute_query(cursor, insert_query, (category_name,))
        category_id = cursor.lastrowid
        category_df.at[index, 'root_category_id'] = int(category_id)
        logger.info(f"'{category_name}' 카테고리가 추가되었습니다. 삽입된 category_id: {category_id}")

    return category_df


def insert_child_categories(cursor, category_df):
    """카테고리 데이터프레임의 각 행을 순회하며 categories 테이블에 한단계 하위 레벨 자식 카테고리 데이터를 insert합니다."""

    for index, row in category_df.iterrows():
        parent_category_id = row['root_category_id']
        category_name = row['2Depth']
        insert_query = "INSERT INTO categories (parent_category_id, category_name) VALUES (%s, %s)"
        execute_query(cursor, insert_query, (int(parent_category_id), category_name,))
        category_id = cursor.lastrowid
        category_df.at[index, 'db_child_category_id'] = int(category_id)
        logger.info(f"'{category_name}' 카테고리가 추가되었습니다.")
    return category_df


def insert_publisher(cursor, publisher_name):
    """publishers 테이블에 출판사 데이터를 insert합니다. 이미 저장된 출판사 데이터인 경우 primary key만을 반환하고, 저장되지 않은 출판사인 경우 데이터를 저장 후 primary
    key를 반환합니다."""
    # 출판사 이름이 이미 데이터베이스에 있는지 확인
    select_query = "SELECT publisher_id FROM publishers WHERE publisher_name = %s"
    execute_query(cursor, select_query, (publisher_name,))
    existing_publisher = cursor.fetchone()

    if existing_publisher:
        publisher_id = existing_publisher[0]
        logger.info(f"이미 '{publisher_name}' 출판사가 데이터베이스에 존재합니다. Primary key: {publisher_id}")
        return publisher_id
    else:
        # 출판사 email은 더미 데이터로 저장함
        publisher_email = generate_dummy_email()
        insert_query = "INSERT INTO publishers (publisher_name, publisher_email) VALUES (%s, %s)"
        execute_query(cursor, insert_query, (publisher_name, publisher_email,))
        inserted_publisher_id = cursor.lastrowid
        logger.info(
            f"출판사 이름 : '{publisher_name}', 출판사 이메일 : '{publisher_email}' 데이터가 추가되었습니다. primary key: {inserted_publisher_id}")
        return inserted_publisher_id


def insert_book_info(cursor, book_info, publisher_id):
    """books 테이블에 도서 데이터를 insert합니다. 추가된 도서의 primary key를 반환합니다."""
    insert_query = ("INSERT INTO books (publisher_id, book_name, book_index, book_desc, book_isbn_13, book_price, "
                    "book_discount, book_package, book_published, book_stock) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,"
                    " %s, %s)")
    execute_query(cursor, insert_query,
                  (publisher_id, book_info['book_name'],
                   preprocessing_book_index(book_info['book_index']), book_info["book_desc"],
                   book_info['book_isbn_13'], book_info['book_price'], generate_book_discount(),
                   generate_book_package(), preprocessing_book_published(book_info['book_published']),
                   generate_book_stock(),))
    inserted_book_id = cursor.lastrowid

    logger.info(f"책 이름 : '{book_info['book_name']}', Primary key : '{inserted_book_id}' 데이터가 추가되었습니다.")
    return inserted_book_id


def insert_book_thumbnail(cursor, book_id, image_url):
    """book_thumbnails 테이블에 썸네일 이미지 데이터를 insert합니다."""
    insert_query = "INSERT INTO book_thumbnails (book_id, thumbnail_image_url) VALUES (%s, %s)"
    execute_query(cursor, insert_query, (book_id, image_url,))

    logger.info(f"book_id : '{book_id}'에 대한 썸네일 이미지 데이터가 추가되었습니다.")


def insert_book_image(cursor, book_id, image_url_list):
    """book_images 테이블에 도서 이미지 데이터를 insert합니다."""
    insert_query = "INSERT INTO book_images (book_id, book_image_url) VALUES (%s, %s)"

    for img_url in image_url_list:
        execute_query(cursor, insert_query, (book_id, img_url,))

    logger.info(f"book_id : '{book_id}'에 대한 미리보기 이미지 데이터가 추가되었습니다.")


def insert_participant(cursor, participant_name):
    """participants 테이블에 도서 참가자 데이터를 insert합니다."""
    select_query = "SELECT participant_id FROM participants WHERE participant_name = %s"
    execute_query(cursor, select_query, (participant_name,))
    existing_book_participant = cursor.fetchone()

    if existing_book_participant:
        return existing_book_participant[0]
    else:
        insert_query = "INSERT INTO participants (participant_name, participant_email) VALUES (%s, %s)"
        execute_query(cursor, insert_query, (participant_name, generate_dummy_email(),))
        inserted_participant_id = cursor.lastrowid

        return inserted_participant_id


def insert_participant_role(cursor, participant_role_name):
    """participant_roles 테이블에 도서 참가자 역할 데이터를 insert합니다."""
    select_query = "SELECT participant_role_id FROM participant_roles WHERE participant_role_name = %s"
    execute_query(cursor, select_query, (participant_role_name,))
    existing_book_participant_role = cursor.fetchone()

    if existing_book_participant_role:
        return existing_book_participant_role[0]
    else:
        insert_query = "INSERT INTO participant_roles (participant_role_name) VALUES (%s)"
        execute_query(cursor, insert_query, (participant_role_name,))
        inserted_participant_role_id = cursor.lastrowid

        return inserted_participant_role_id


def insert_participant_role_registration(cursor, book_id, participant_id, participant_role_id):
    """participant_role_registration 테이블에 도서 참가자 역할 등록 데이터를 insert합니다."""
    insert_query = "INSERT INTO participant_role_registrations (participant_id, participant_role_id, book_id) VALUES (%s, %s, %s)"
    execute_query(cursor, insert_query, (participant_id, participant_role_id, book_id))

def insert_book_category(cursor, book_id, category_id):
    """book_categories 테이블에 도서와 카테고리의 맵핑 데이터를 insert합니다."""
    insert_querty = "INSERT INTO book_categories (book_id, category_id) VALUES (%s, %s)"
    execute_query(cursor, insert_querty, (book_id, category_id, ))

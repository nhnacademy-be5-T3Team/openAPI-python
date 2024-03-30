
import pymysql
import secret
from openAPI.dummy_data_maker import *


def getConnection():
    """데이터베이스에 연결하고 커서를 반환합니다."""

    conn = pymysql.connect(
        host=secret.host,
        user=secret.user,
        password=secret.password,
        db=secret.database)
    print("MySQL 데이터베이스에 연결되었습니다.")
    return conn, conn.cursor()


def execute_query(cursor, query, data=None):
    """주어진 쿼리를 실행합니다."""
    if data:
        cursor.execute(query, data)
    else:
        cursor.execute(query)


def insert_parent_categories(cursor, category_df):
    """카테고리 데이터프레임의 각 행을 순회하며 categories 테이블에 최상위 계층 부모 카테고리 데이터를 insert하고 primary key 값을 dataframe으로 return 합니다."""
    for index, row in category_df.iterrows():
        category_name = row['1Depth']
        insert_query = "INSERT INTO categories (category_name) VALUES (%s)"
        execute_query(cursor, insert_query, (category_name,))
        category_id = cursor.lastrowid
        category_df.at[index, 'root_category_id'] = int(category_id)
        print(f"'{category_name}' 카테고리가 추가되었습니다. 삽입된 category_id: {category_id}")

    return category_df


def insert_child_categories(cursor, category_df):
    """카테고리 데이터프레임의 각 행을 순회하며 categories 테이블에 한단계 하위 레벨 자식 카테고리 데이터를 추가합니다."""
    for index, row in category_df.iterrows():
        parent_category_id = row['root_category_id']
        category_name = row['2Depth']
        insert_query = "INSERT INTO categories (parent_category_id, category_name) VALUES (%s, %s)"
        execute_query(cursor, insert_query, (int(parent_category_id), category_name,))

        print(f"'{category_name}' 카테고리가 추가되었습니다.")


def insert_publisher(cursor, publisher_name):
    # 출판사 이름이 이미 데이터베이스에 있는지 확인
    select_query = "SELECT publisher_id FROM publishers WHERE publisher_name = %s"
    cursor.execute(select_query, (publisher_name,))
    existing_publisher = cursor.fetchone()

    if existing_publisher:
        publisher_id = existing_publisher[0]
        print(f"이미 '{publisher_name}' 출판사가 데이터베이스에 존재합니다. Primary key: {publisher_id}")
        return publisher_id
    else:
        publisher_email = generate_dummy_email()
        insert_query = "INSERT INTO publishers (publisher_name, publisher_email) VALUES (%s, %s)"
        cursor.execute(insert_query, (publisher_name, publisher_email,))
        inserted_publisher_id = cursor.lastrowid
        print(f"출판사 이름 : '{publisher_name}', 출판사 이메일 : '{publisher_email}' 데이터가 추가되었습니다. primary key: {inserted_publisher_id}")
        return inserted_publisher_id

def insert_book_info(cursor, book_info, publisher_id):

    insert_query = "INSERT INTO books (publisher_id, book_name, book_index, book_desc, book_isbn_13, book_price, book_discount, book_package, book_published, book_stock) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    execute_query(cursor, insert_query,
                  (publisher_id, book_info['book_name'],
                   preprocessing_book_index(book_info['book_index']), book_info["book_desc"],
                   book_info['book_isbn_13'], book_info['book_price'], generate_book_discount(),
                   generate_book_package(), preprocessing_book_published(book_info['book_published']), generate_book_stock(),))
    inserted_book_id = cursor.lastrowid

    print(f"책 이름 : '{book_info['book_name']}', Primary key : '{inserted_book_id}' 데이터가 추가되었습니다.")
    return inserted_book_id
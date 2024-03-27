
import pymysql
import secret

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

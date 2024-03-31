import pandas as pd
from mysql.insert_query import *
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def xls_to_df(file_path):
    """카테고리 xls 파일을 읽어, 최상위 부모 카테고리 dataframe과 한단계 하위 레벨 자식 카테고리 dataframe으로 분류합니다."""

    df = pd.read_excel(file_path, header=2)
    df = df.fillna(0)

    # '국내도서'인 행들만 필터링하여 dataframe 생성
    domestic_books_df = df[(df['몰'] == '국내도서') & (df['1Depth'] != 'Gift')]

    # 최상위 계층 부모 카테고리 dataframe 생성
    root_category = domestic_books_df[domestic_books_df['2Depth'] == 0][['CID', '1Depth']]

    # 한단계 하위 레벨 자식 카테고리
    child_cateogry = domestic_books_df[(domestic_books_df['3Depth'] == 0) & (domestic_books_df['2Depth'] != 0)][
        ['CID', '1Depth', '2Depth']]

    return root_category, child_cateogry


def save_df_to_csv(category_df, file_name):
    """dataframe 파일을 resources 디렉토리 아래의 csv 파일로 저장합니다."""
    # 저장할 폴더 경로 설정
    folder_path = 'resources'

    # 폴더가 존재하지 않으면 생성
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 파일 경로 설정
    file_path = os.path.join(folder_path, file_name)

    # 데이터프레임을 CSV 파일로 저장
    category_df.to_csv(file_path, index=False)


if __name__ == "__main__":

    file_name = "aladin_Category_CID_20200626.xls"
    file_path = os.path.join(os.getcwd(), '../resources/', file_name)
    root_category, child_category = xls_to_df(os.path.abspath(file_path))

    conn, cursor = get_connection()

    root_category_id_df = []
    if conn and cursor:
        # 최상위 계층 부모 카테고리 데이터 insert, PrimaryKey category_id 저장
        root_category_id_df = insert_parent_categories(cursor, root_category)

        # 커밋 및 연결 종료
        conn.commit()
        conn.close()
        print("MySQL 연결이 닫혔습니다.")

        save_df_to_csv(root_category_id_df, 'root_category_id_df.csv')

    # child_category dataframe의 부모 카테고리 정보를 root_category_id_df와 맵핑합니다.
    mapped_child_category = pd.merge(child_category, root_category_id_df, on='1Depth', how='left')

    # mapping이 되지 않은 값 확인
    unmapped_values = mapped_child_category[mapped_child_category['root_category_id'].isnull()]['1Depth'].tolist()
    logger.info("Mapping 되지 않은 값:", unmapped_values)

    # mapping이 되지 않은 값 삭제
    mapped_child_category = mapped_child_category.dropna(subset=['root_category_id'])

    save_df_to_csv(mapped_child_category, 'mapped_child_category.csv')

    conn, cursor = get_connection()
    if conn and cursor:
        # 한단계 하위 레벨 자식 카테고리 데이터 insert
        category_df = insert_child_categories(cursor, mapped_child_category)

        save_df_to_csv(category_df, 'mapped_child_category.csv')

        # 커밋 및 연결 종료
        conn.commit()
        conn.close()
        logger.info("MySQL 연결이 닫혔습니다.")

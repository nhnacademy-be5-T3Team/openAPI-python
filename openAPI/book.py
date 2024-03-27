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
    # csv_file_path = 'resources/mapped_child_category.csv'
    # df = pd.read_csv(csv_file_path)
    #
    # isbn_list = isbn_list_by_category_id()

    isbn_list = [{'category_name': '가계부', 'category_id': 90452, 'isbn_list': ['8809984880002', '8809983390007', '8809479920732', '8809529015272', '8809529015258', '8809529015265', '9788960306257', '8809850420028', '8809637010237', '8809637010220']}, {'category_name': '건강요리', 'category_id': 53471, 'isbn_list': ['9791189529116', '9788984688803']}]

    for item in isbn_list:
        isbns = item['isbn_list']
        print(isbns)

        for isbn in isbns:
            print(isbn)
            result = openAPI_request_detail(isbn)
            print(result)
            break

        break
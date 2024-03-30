# openAPI_python

본 파이썬 모듈은 NHNAcademy be5 T3Team의 팀 프로젝트에서 테스트 데이터 삽입을 위해 사용됩니다. <br>
알라딘 OpenAPI에 접근하여 도서 정보를 추출하고, 이를 MySQL 데이터베이스에 삽입하는 기능을 제공합니다

### 기능 
1. category 추출 및 데이터베이스 insert
- 알라딘 OpenAPI 메뉴얼에서 제공하는 '알라딘 전분야 카테고리 (2021.09.27)'의 엑셀 파일에서 필요한 깊이의 카테고리 정보를 추출합니다.
- 최상단 root 카테고리와 한단계 깊이의 자식 카테고리를 구분해 데이터베이스에 insert 합니다.

2. 알라딘 OpenAPI 연동 및 도서 관련 데이터 insert 기능
- 추출한 카테고리 정보를 기반으로 알라딘 OpenAPI의 '상품 검색 API'를 사용하여 도서 정보를 요청합니다.
- 응답받은 데이터를 파싱한 후 필요한 정보를 데이터베이스에 insert합니다. 


### how to use

1. python 가상 환경 구성
    
    ```bash
    python -m venv myenv
    
    source myenv/bin/activate
    
    pip install -r requirements.txt
    ```
    
2. secret.py 구성
    ```bash
   host = "데이터베이스 url 주소"
   user = "데이터베이스 user 이름"
   password = "데이터베이스 password"
   database = "데이터베이스 이름"
   aladin_open_api_ttbkey = "알라딘 Open API 신청 key"
   aladin_open_api_search_url = "알라딘 Open API 도서 검색 url"
   aladin_open_api_detail_url = "알라딘 Open API 도서 상세 조회 url"
    ```

3. category.py 스크립트 실행 
4. book.py 스크립트 실행
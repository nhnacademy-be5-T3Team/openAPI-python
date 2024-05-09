# object.py
import os
import requests
import logging
import secret

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObjectService:
    def __init__(self, storage_url, token_id):
        self.storage_url = storage_url
        self.token_id = token_id

    def _get_url(self, foldername, container, object):
        return '/'.join([self.storage_url, container, foldername, object])

    def _get_request_header(self):
        return {'X-Auth-Token': self.token_id}

    def upload(self, container, foldername, object, object_path):
        req_url = self._get_url(foldername, container, object)
        req_header = self._get_request_header()

        path = '/'.join([object_path, object])
        with open(path, 'rb') as f:
            response = requests.put(req_url, headers=req_header, data=f.read())
            if response.status_code == 201:
                logger.info("요청이 성공적으로 처리되었습니다. 상태코드 : {}", response.status_code)
            else:
                logger.info("실패 요청 : {}", response.status_code)


if __name__ == '__main__':
    STORAGE_URL = secret.object_storage_upload_url
    CONTAINER_NAME = secret.object_storage_container_name
    TOKEN_ID = ''  # auth.py 실행으로 얻은 토큰 id를 넣어주세요
    FOLDER_NAME = 'book_thumbnails'  # book_thumbnails, book_images
    OBJECT_PATH = os.path.join(str(os.path.dirname(os.path.dirname(__file__))), "openAPI", "resources", "book_images")  # 이미지 파일 위치

    cnt = 0
    for filename in os.listdir(OBJECT_PATH):
        OBJECT_NAME = filename

        obj_service = ObjectService(STORAGE_URL, TOKEN_ID)

        obj_service.upload(CONTAINER_NAME, FOLDER_NAME, OBJECT_NAME, OBJECT_PATH)
        cnt = cnt + 1
        logger.info("cnt : {} | object name : {}", cnt, OBJECT_NAME)

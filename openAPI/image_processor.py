import requests
import os
import csv
import uuid
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_unique_filename(image_url):
    """UUID를 사용하여 고유한 파일 이름 생성하는 함수"""
    image_uuid = str(uuid.uuid4())
    image_extension = image_url.split('.')[-1]
    image_filename = f"{image_uuid}.{image_extension}"
    return image_filename


def save_to_csv(image_filename, book_id, save_folder):
    """CSV에 매핑 정보 저장하는 함수"""
    save_csv_name = "image_book_mapping_" + save_folder + ".csv"
    save_csv_path = os.path.join(os.path.dirname(__file__), "resources", save_csv_name)
    with open(os.path.join(save_csv_path), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([image_filename, book_id])


def download_image(image_url, save_folder, book_id):
    """이미지를 다운로드하고 저장하는 함수"""

    # 다운로드 받을 이미지를 저장할 폴더
    download_img_folder = os.path.join(str(os.path.dirname(__file__)), "resources", save_folder)

    # 이미지 다운로드 요청
    response = requests.get(image_url)

    if response.status_code == 200:
        image_filename = generate_unique_filename(image_url)

        save_path = os.path.join(download_img_folder, image_filename)

        with open(save_path, 'wb') as f:
            f.write(response.content)
        logger.info("이미지 다운로드 완료 : {}", save_path)

        # CSV에 매핑 정보 저장
        save_to_csv(image_filename, book_id, save_folder)

        return image_filename
    else:
        logger.info("이미지 다운로드 실패 : {}", response.status_code)


def save_random_image(save_folder, book_id):
    """이미지를 랜덤으로 선택해 저장하는 함수"""
    # 다운로드 받을 이미지를 저장할 폴더
    download_img_folder = os.path.join(str(os.path.dirname(__file__)), "resources", save_folder)
    # 랜덤 이미지를 선택할 폴더
    random_img_folder = os.path.join(str(os.path.dirname(os.path.dirname(__file__))), "resources", "test_img")

    image_files = [f for f in os.listdir(random_img_folder) if os.path.isfile(os.path.join(random_img_folder, f))]

    if not image_files:
        logger.error("폴더 내에 이미지가 없습니다.")
        return None

    selected_image_file = random.choice(image_files)

    img_name = generate_unique_filename(selected_image_file)

    image_path = os.path.join(random_img_folder, selected_image_file)
    save_path = os.path.join(download_img_folder, img_name)
    # 이미지 파일 복사하여 저장
    with open(save_path, 'wb') as dest, open(image_path, 'rb') as src:
        dest.write(src.read())

    save_to_csv(img_name, book_id, save_folder)
    logger.info("이미지 다운로드 완료 : {}", save_path)

    return img_name

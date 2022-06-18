import requests
import os
import random

from dotenv import load_dotenv


def get_xkcd_comics(comics_number):
    response = requests.get(f"https://xkcd.com/{comics_number}/info.0.json")
    comment = response.json()["alt"]
    image_link = response.json()["img"]
    image_content = requests.get(response.json()["img"])
    with open("image.png", "wb") as file:
        file.write(image_content.content)
    return comment


def get_upload_server(vk_api_token, group_id):
    params = {"access_token": vk_api_token, "v": "5.131", "group_id": group_id}
    response = requests.get("https://api.vk.com/method/photos.getWallUploadServer", params=params)
    return response.json()["response"]["upload_url"]


def upload_image(upload_url):
    with open("image.png", "rb") as file:
        files = {'photo': file}
        response = requests.post(url=upload_url, files=files)
    response_content = response.json()
    return response_content["photo"], response_content["server"], response_content["hash"]


def save_wall_photo(vk_api_token, photo, server, hash, group_id):
    params = {"access_token": vk_api_token, "v": "5.131", "photo": photo, "server": server, "hash": hash, "group_id": group_id}
    response = requests.post("https://api.vk.com/method/photos.saveWallPhoto", params=params)
    full_response = response.json()["response"][0]
    return full_response["id"], full_response["owner_id"]


def make_wall_post(vk_api_token, group_id, message, owner_id, photo_id):
    params = {"access_token": vk_api_token, "v": "5.131", "owner_id": -group_id, "from_group": 1, "message": message, "attachments": f"photo{owner_id}_{photo_id}"}
    response = requests.post("https://api.vk.com/method/wall.post", params=params)
    print(response.text)


def get_total_comics_num():
    response = requests.get("https://xkcd.com/info.0.json")
    response.raise_for_status()
    return response.json()["num"]


def main():
    load_dotenv()
    vk_api_key = os.getenv("VK_API_KEY")
    group_id = os.getenv("VK_GROUP_ID")
    top_number = get_total_comics_num()
    comment = get_xkcd_comics(random.randint(1, top_number))
    upload_url = get_upload_server(vk_api_key, group_id)
    photo, server, hash = upload_image(upload_url)
    photo_id, owner_id = save_wall_photo(vk_api_key, photo, server, hash, group_id)
    make_wall_post(vk_api_key, group_id, comment, owner_id, photo_id)
    os.remove("image.png")

if __name__ == "__main__":
    main()

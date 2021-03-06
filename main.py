import os
import random
import logging
from urllib.error import HTTPError
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


class VK_API_Error(Exception):
    pass


def check_for_error_in_response(response):
    """Check for error in response."""
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise VK_API_Error(payload["error"]["error_msg"])


def get_xkcd_comics(comics_number):
    """Download xkcd comics under specific number.

    ACCEPTS:
        comics_number (int): XKCD comics number
    RETURNS:
        comment (str): Image caption text
        file_name (str): Image file name
    """
    response = requests.get(f"https://xkcd.com/{comics_number}/info.0.json")
    response.raise_for_status()
    payload = response.json()
    comment = payload["alt"]
    image_link = payload["img"]
    file_name = urlparse(image_link).path.rpartition('/')[-1]
    response = requests.get(image_link)
    response.raise_for_status()
    with open(file_name, "wb") as file:
        file.write(response.content)
    return comment, file_name


def get_upload_server(vk_api_token, group_id):
    """Get upload server url from VK.

    ACCEPTS:
        vk_api_token (str): VK API token
        group_id (str): VK Group id number
    RETURNS:
        (str) Url for image upload
    """
    params = {"access_token": vk_api_token, "v": "5.131", "group_id": group_id}
    response = requests.get(
        "https://api.vk.com/method/photos.getWallUploadServer",
        params=params
    )
    check_for_error_in_response(response)
    return response.json()["response"]["upload_url"]


def upload_image(upload_url, file_name):
    """Upload image to VK using upload url.

    ACCEPTS:
        upload_url (str): Url received from VK for image upload
        file_name (str): Image filename
    RETURNS:
       (str) Information about uploaded image
       (str) Server id
       (str) Image hash
    """
    with open(file_name, "rb") as file:
        files = {'photo': file}
        response = requests.post(url=upload_url, files=files)
    check_for_error_in_response(response)
    payload = response.json()
    return payload["photo"], payload["server"], payload["hash"]


def save_wall_photo(vk_api_token, photo, server, image_hash, group_id):
    """Save wall photo in VK.

    ACCEPTS:
        vk_api_token (str): VK API token
        photo (str): Information about uploaded image
        server (str): Server id
        image_hash (str): Image hash
        group_id (str): VK Group id number
    RETURNS:
        (str): Image id
        (str): Image owner id
    """
    params = {
        "access_token": vk_api_token,
        "v": "5.131",
        "photo": photo,
        "server": server,
        "hash": image_hash,
        "group_id": group_id
    }
    response = requests.post(
        "https://api.vk.com/method/photos.saveWallPhoto",
        params=params
    )
    check_for_error_in_response(response)
    payload = response.json()["response"][0]
    return payload["id"], payload["owner_id"]


def make_wall_post(vk_api_token, group_id, message, owner_id, photo_id):
    """Post image to wall.

    ACCEPTS:
        vk_api_token (str): VK API token
        group_id (str): VK Group id number
        message (str): Image caption text
        owner_id (str): Image owner id
        photo_id (str): Image id
    RETURNS
        (int): VK post id
    """
    params = {
        "access_token": vk_api_token,
        "v": "5.131",
        "owner_id": f"-{group_id}",
        "from_group": 1,
        "message": message,
        "attachments": f"photo{owner_id}_{photo_id}"
    }
    response = requests.post(
        "https://api.vk.com/method/wall.post",
        params=params
    )
    check_for_error_in_response(response)
    return response.json()["response"]["post_id"]


def get_total_comics_num():
    """Return the total number of available XKCD comics.

    ACCEPTS:
       None
    RETURNS:
       (int) The number of the last available comics
    """
    response = requests.get("https://xkcd.com/info.0.json")
    response.raise_for_status()
    return response.json()["num"]


def main():
    """Main function."""
    load_dotenv()
    vk_api_key = os.getenv("VK_API_KEY")
    group_id = os.getenv("VK_GROUP_ID")
    top_number = get_total_comics_num()
    comment, file_name = get_xkcd_comics(random.randint(1, top_number))
    try:
        upload_url = get_upload_server(vk_api_key, group_id)
        photo, server, image_hash = upload_image(upload_url, file_name)
        photo_id, owner_id = save_wall_photo(
            vk_api_key,
            photo,
            server,
            image_hash,
            group_id
        )
        make_wall_post(vk_api_key, group_id, comment, owner_id, photo_id)
    except (HTTPError, ConnectionError, VK_API_Error) as err:
        logging.error(err)
    finally:
        os.remove(file_name)


if __name__ == "__main__":
    main()

import requests
from typing import Optional

def _check_if_link_is_working(url: str) -> Optional[str]:
    try:
        response = requests.head(url, allow_redirects=True)

        return url if 200 <= response.status_code < 400 else None
    except requests.exceptions.RequestException as e:
        return None

def generate_pegi3s_url(image_data) -> Optional[str]:
    return f"https://hub.docker.com/r/pegi3s/{image_data['name']}/"

def generate_github_url(image_data) -> Optional[str]:
    return _check_if_link_is_working(f"https://github.com/pegi3s/dockerfiles/tree/master/{image_data['name']}/")

def generate_source_url(image_data) -> Optional[str]:
    if "source_url" in image_data and len(image_data["source_url"].strip()) == 0:
        return image_data["source_url"]
    else:
        return None

def generate_manual_url(image_data) -> Optional[str]:
    return image_data["manual_url"]

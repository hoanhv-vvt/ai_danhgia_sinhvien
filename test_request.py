import requests

def test_extract_api():
    url = "http://0.0.0.0:8188/api/extract"

    # Endpoint nhận Form data (images: List[str] = Form(None))
    # Gửi nhiều URL bằng cách lặp lại key "images"
    form_data = [
        # ("images", "https://www.flickr.com/photos/199095271@N05/55124349890/sizes/z/"),
        # ("images", "https://www.flickr.com/photos/199095271@N05/55123955326/sizes/z/"),
        ("images", "https://live.staticflickr.com/65535/55123962491_c8a541feeb_c.jpg"),
    ]

    try:
        response = requests.post(url, data=form_data)
        response.raise_for_status()
        print("Status Code:", response.status_code)
        print("Response Body:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print("Server detail:", e.response.text)

if __name__ == "__main__":
    test_extract_api()


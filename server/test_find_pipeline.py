import requests
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
FIND_URL = f"{BACKEND_URL}/api/v1/find/find"

# Path to a small test video file
TEST_VIDEO_PATH = "titan/public/test/adolasence-teaser.mp4"
QUERY = "you dont think youre pretty"

def test_find_pipeline():
    if not os.path.exists(TEST_VIDEO_PATH):
        print(f"❌ Test video not found: {TEST_VIDEO_PATH}")
        return
    with open(TEST_VIDEO_PATH, "rb") as f:
        files = {"video": (os.path.basename(TEST_VIDEO_PATH), f, "video/mp4")}
        data = {"query": QUERY}
        print(f"POST {FIND_URL} ...")
        resp = requests.post(FIND_URL, files=files, data=data)
        print(f"Status: {resp.status_code}")
        try:
            print("Response:", resp.json())
        except Exception:
            print("Raw response:", resp.text)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            for i, clip in enumerate(results):
                print(f"Clip {i+1}: {clip.get('video_url')} | {clip.get('start')} - {clip.get('end')}")
        else:
            print("❌ Pipeline failed!")

if __name__ == "__main__":
    test_find_pipeline() 
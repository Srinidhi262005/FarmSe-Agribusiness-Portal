import requests
import os

images = {
    "green_chilli.png": "https://images.pexels.com/photos/4033296/pexels-photo-4033296.jpeg?auto=compress&cs=tinysrgb&w=800",
    "millets.png": "https://images.unsplash.com/photo-1628151525942-835688a21e7d?auto=format&fit=crop&w=800&q=80",
    "rice.png": "https://images.unsplash.com/photo-1591871937573-74dbba515c4c?auto=format&fit=crop&w=800&q=80",
    "onion.png": "https://images.unsplash.com/photo-1580201092675-a0a6a6cafbb1?auto=format&fit=crop&w=800&q=80",
    "vegetables.png": "https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?auto=format&fit=crop&w=800&q=80",
    "apple.png": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=800&q=80"
}

target_dir = "app/static/crop_images"
os.makedirs(target_dir, exist_ok=True)

for filename, url in images.items():
    print(f"Downloading {filename}...")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(os.path.join(target_dir, filename), 'wb') as f:
                f.write(response.content)
            print(f"Successfully saved {filename}")
        else:
            print(f"Failed to download {filename}: Status {response.status_code}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

print("Done!")

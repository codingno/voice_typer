import urllib.request
import re

url = "https://alphacephei.com/vosk/models"
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0'}
)

try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
        # Let's search for any link ending in .zip that contains "id" or "indonesian"
        links = re.findall(r'href="([^"]+\.zip)"', html)
        print("Found ZIP links:")
        found = False
        for link in links:
            if "id" in link.split('/')[-1] or "indonesian" in link.lower():
                print(f"-> {link}")
                found = True
        if not found:
            print("No Indonesian model links found in the main list. Let's dump all zip links containing 'small':")
            for link in links:
                if "small" in link:
                    print(f"  {link}")
except Exception as e:
    print(f"Error: {e}")

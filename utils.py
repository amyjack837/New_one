import re

def extract_links(text):
    if not text:
        return []
    return re.findall(r'https?://[^\s]+', text)

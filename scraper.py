import requests
from bs4 import BeautifulSoup
import json

url = "https://books.toscrape.com/catalogue/page-1.html"

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
books_data = []
book_cards = soup.find_all('article', class_='product_pod')

for card in book_cards:
    title = card.find('h3').find('a')['title']
    price = card.find('p', class_='price_color').text
    link = card.find('h3').find('a')['href']
    base_url = url
    full_link = requests.compat.urljoin(base_url, link)

    books_data.append({
        "title": title,
        "price": price,
        "link": full_link
    })

result = {"books": books_data}

with open('books.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=4, ensure_ascii=False)

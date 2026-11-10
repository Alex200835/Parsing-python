import requests
from bs4 import BeautifulSoup
import json
import psycopg2
from datetime import datetime
import re

conn = psycopg2.connect(host="localhost", port="5432", dbname="booksdb", user="postgres", password="postgres")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY, 
        name TEXT, 
        url TEXT, 
        price REAL, 
        found_on_page INT, 
        found_at TIMESTAMP
    );
""")
conn.commit()

url = "https://books.toscrape.com/catalogue/page-1.html"
page_num = 1
first_page_books = [] # Сюда сохраним данные только с 1-й страницы для JSON

while url:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    current_page_books = []
    
    for card in soup.find_all('article', class_='product_pod'):
        title = card.find('h3').find('a')['title']
        link = card.find('h3').find('a')['href']
        full_link = requests.compat.urljoin(url, link)
        
        price_raw = card.find('p', class_='price_color').text
        price = float(re.sub(r'[^\d.]', '', price_raw))
        
        current_page_books.append({
            "title": title,
            "price": price,
            "link": full_link
        })
        
        cursor.execute("""
            INSERT INTO books (name, url, price, found_on_page, found_at) 
            VALUES (%s, %s, %s, %s, %s)
        """, (title, full_link, price, page_num, datetime.now()))
        
    conn.commit()

    if page_num == 1:
        first_page_books = current_page_books

    next_btn = soup.find('li', class_='next')
    url = requests.compat.urljoin(url, next_btn.find('a')['href']) if next_btn else None
    page_num += 1

cursor.close()
conn.close()

with open('books.json', 'w', encoding='utf-8') as f:
    json.dump({"books": first_page_books}, f, indent=4, ensure_ascii=False)

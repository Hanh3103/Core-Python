import os
import string

import requests
from bs4 import BeautifulSoup

msg1 = "Input the URL:"


class WebScrapper:
    def __init__(self, pagenumber, article_type):
        self.page_number = pagenumber
        self.url = "https://www.nature.com/nature/articles?sort=PubDate&year=2020"
        self.article_type = article_type

    # def check_url(self):
    #     if "nature.com" in self.url:
    #         return True
    #     else:
    #         print("Invalid page!")
    #         return False

    # def send_request(self):
    #     self.response = requests.get(self.url, headers={'Accept-Language': 'en-US,en;q=0.5'})

    def create_response(self):
        for number in range(self.page_number + 1):
            page_url = self.url + "&page=" + str(number)
            page_response = requests.get(page_url, headers={'Accept-Language': 'en-US,en;q=0.5'})
            if page_response.status_code == 200:
                folder_name = f'Page_{number}'
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)

                soup = BeautifulSoup(page_response.content, 'html.parser')
                articles = soup.find_all('article')
                for article in articles:
                    article_type = article.find('span', {'data-test': 'article.type'}).text.strip()

                    if article_type == self.article_type:
                        article_link = article.find('a', {'data-track-action': 'view article'})['href']
                        article_title = article.find('a', {'data-track-action': 'view article'}).text.strip()
                        self.save_article(article_link, article_title, folder_name)
            else:
                print("The URL returned " + str(page_response.status_code))
        print("Saved all articles")

    @staticmethod
    def save_article(article_link, article_title, folder):
        article_url = 'https://www.nature.com' + article_link
        article_response = requests.get(article_url)
        article_soup = BeautifulSoup(article_response.content, 'html.parser')

        article_content = article_soup.find('div', {'class': 'c-article-body'}).text.strip()
        article_filename = \
            article_title.translate(str.maketrans('', '', string.punctuation)).replace(' ', '_') + '.txt '

        # folder_name = f'Page_{page_num}/Folder_{self.article_type}'
        # if not os.path.exists(folder_name):
        #     os.makedirs(folder_name)
        with open(os.path.join(folder, article_filename), 'w', encoding="UTF-8") as f:
            f.write(article_content)


if __name__ == '__main__':
    page_number = int(input())
    article_typ = input()
    a = WebScrapper(page_number, article_typ)
    a.create_response()

import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class UrlParser(object):
    def __init__(self):
        self.session = requests.Session()
        # Словарь с заголовками для http-запроса
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/74.0.3729.169 Safari/537.36",
            "Accept-Language": "ru",
        }

    @staticmethod
    def text_formatting(parsed_text: str) -> str:
        """Форматирует текст распаршенной статьи."""

        start_index = 0
        end_index = 80
        while end_index < len(parsed_text):
            if parsed_text.rfind("\n", start_index, end_index) != -1:
                start_index = parsed_text.rfind("\n", start_index, end_index) + 1
                end_index = start_index + 80
                continue
            else:
                if parsed_text.rfind(" ", start_index, end_index) != -1:
                    start_index = parsed_text.rfind(" ", start_index, end_index)
                    parsed_text = (
                        parsed_text[: start_index + 1]
                        + "\n"
                        + parsed_text[start_index + 1 :]
                    )
                elif parsed_text.rfind("-", start_index, end_index) != -1:
                    start_index = parsed_text.rfind("-", start_index, end_index)
                    parsed_text = (
                        parsed_text[: start_index + 1]
                        + "\n"
                        + parsed_text[start_index + 1 :]
                    )
                elif parsed_text.rfind("/", start_index, end_index) != -1:
                    start_index = parsed_text.rfind("/", start_index, end_index)
                    parsed_text = (
                        parsed_text[: start_index + 1]
                        + "\n"
                        + parsed_text[start_index + 1 :]
                    )
                end_index = start_index + 80
        return parsed_text

    def get_page(self, url: str) -> str:
        """Возвращает html-код страницы с указанного URL"""
        page = self.session.get(url)
        return page.text

    def parse_page(self, url: str) -> str:
        """Парсит страницу находящуюся на указанном URL"""
        filtered_news = ""
        filtered_all_news = ""
        all_news = []
        item_index = 0
        page_text = self.get_page(url)
        soup = BeautifulSoup(page_text, "html.parser")
        hostname = urlparse(url).hostname
        with open("config.json") as config:
            parser = json.load(config)

        hostname = hostname.replace(".ru", "")
        resource = hostname.replace("www.", "")

        for item in parser:
            if item.get("resource") == resource:
                break
            item_index += 1

        # заголовок
        try:
            filtered_news += (
                soup.find(
                    parser[item_index]["title"]["tag"],
                    class_=parser[item_index]["title"]["class"],
                )
                .find(
                    parser[item_index]["title"]["secondTag"],
                    class_=parser[item_index]["title"]["secondClass"],
                )
                .text.strip()
                + "\n\n"
            )
        except (AttributeError, KeyError):
            pass
        # подзаголовок или интро
        try:
            filtered_news += (
                soup.find(
                    parser[item_index]["subtitle"]["tag"],
                    class_=parser[item_index]["subtitle"]["class"],
                )
                .find(
                    parser[item_index]["subtitle"]["secondTag"],
                    class_=parser[item_index]["subtitle"]["secondClass"],
                )
                .text.strip()
                + "\n\n"
            )
        except AttributeError:
            pass
        # текст статьи
        try:
            all_news = soup.find(
                parser[item_index]["text"]["tag"],
                class_=parser[item_index]["text"]["class"],
            ).findAll(parser[item_index]["text"]["secondTag"])
        except KeyError:
            all_news = soup.findAll(
                parser[item_index]["text"]["tag"],
                class_=parser[item_index]["text"]["class"],
            )
        except:
            pass

        for data in all_news:
            filtered_all_news += str(data) + "\n\n"

        for ch in [
            "[",
            "]",
            '<p class="topic-body__content-text">',
            "</a>",
            "</p>",
            '="_blank">',
            "<strong>",
            "/<strong>",
            "<p>",
            '<div class="article__text">',
            "</div>",
            '<span class="idea">',
            "<b>",
            '<a data-auto="true"',
            "</b>",
            "</span>",
            "<a ",
            'class="source" ',
            "</strong>",
            '<p class="topic-body__content-text _lead">',
            "<i>",
            "</i>",
            '<div class="b_article-text" itemprop="articleBody">',
            "class=",
            '"tag"',
            "<u>",
            "</u>",
            "<br/>",
        ]:
            filtered_all_news = filtered_all_news.replace(ch, "")

        filtered_all_news = (
            filtered_all_news.replace('href="', "[")
            .replace('" target', "]")
            .replace('">', "]")
        )

        filtered_news += filtered_all_news

        filtered_news = self.text_formatting(filtered_news)
        return filtered_news

    def file_write(self, url: str) -> str:
        """Формирует текстовый файл с текстом статьи, представленной на указанном URL"""
        file_title = str(url).replace("/", ".")
        start_pos = file_title.find("lenta")
        if start_pos == -1:
            start_pos = file_title.find("gazeta")
            if start_pos == -1:
                start_pos = file_title.find("ria")

        with open(f"{file_title[start_pos:]}.txt", "w") as file:
            file.write(self.parse_page(url))

        return file_title


if __name__ == "__main__":
    url = str(input("Вставьте ссылку на статью: "))
    news_text = UrlParser()
    news_text.file_write(url)
    print(f"Файл успешно создан в папке с программой")

import json
import os
import cloudscraper
from bs4 import BeautifulSoup
import requests

scraper = cloudscraper.create_scraper(browser='chrome', delay=7)

class Mangakakalot:
    
    def __init__(self):
        self.genres = {}
        self.header = {
            "Referer": "https://readmanganato.com/",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'
        }
        self.__load_genres()
        return
    
    
    def get_genre_link(self, genre: str = "ALL") -> str:
        """Get the genre link for a given genre!

        Args:
            genre (str): Genre name.
            state (str, optional): Genre Link state for genre="ALL" only. Defaults to None.
            type (str, optional): Genre Link type, for genre="ALL" Only. Defaults to None.

        Raises:
            ValueError: If invalid name is give or if the genre does not exists.

        Returns:
            str: Returns the genre link.
        """
        try:
            link = self.genres[genre.upper()]
        except KeyError:
            raise ValueError("Invalid genre")
        return link


    def get_recent_updates(self, page_limit: int = 1) -> dict:
        """Get the recently added manga.

        Args:
            page_limit (int, optional): No. of pages to get results from. Defaults to 1.

        Returns:
            dict: Returns a dict containing multiple dicts.
        """
        recent_data = {}
        i = 1
        for n in range(1, page_limit + 1):
            url = f"https://mangakakalot.com/manga_list?type=latest&category=all&state=all&page={str(n)}"
            response = scraper.get(url).text
            soup = BeautifulSoup(response, 'lxml')
            div_lst = soup.find("div", attrs={"class":"truyen-list"}).find_all("div", attrs={"class":"list-truyen-item-wrap"})
            for div in div_lst:
                nsoup = BeautifulSoup(str(div), 'lxml')
                img = nsoup.find("img")['src']
                title, url = nsoup.find("h3").find("a").text, nsoup.find("h3").find("a")['href']
                lch = nsoup.find_all("a")[2].text
                recent_data[str(i)] = {
                    "Title": title,
                    "Cover": img,
                    "Url": url,
                    "Latest_Chapter": lch
                }
                i += 1
        return recent_data


    def search_manga(self, name: str, page_limit: int = 1):
        """Search for a manga

        Args:
            name (str): Name of the manga.
            page_limit (int, optional): No. of pages to get results from. Defaults to 1.
        Returns:
            dict: Returns a dict containing multiple dicts.
        """
        search_data = {}
        fname = name.replace(" ", "_").replace("!", "").replace(",", "").replace("?", "").replace("~", "").replace("|", "").replace("(", "").replace(")", "")
        i = 1
        for n in range(1, page_limit + 1):
            url = f"https://mangakakalot.com/search/story/{fname}?page={n}"
            response = scraper.get(url).text
            soup = BeautifulSoup(response, 'lxml')
            div_lst = soup.find("div", attrs={"class":"panel_story_list"}).find_all("div", attrs={"class":"story_item"})
            for div in div_lst:
                nsoup = BeautifulSoup(str(div), 'lxml')
                img = nsoup.find("img")['src']
                title = nsoup.find("h3").find("a").text
                url = nsoup.find("h3").find("a")['href']
                chap = nsoup.find_all("em", attrs={"class":"story_chapter"})[0].find("a").text.strip()
                search_data[str(i)] = {
                    "Title": title,
                    "Cover": img,
                    "Url": url,
                    "Latest_Chapter": chap
                }
                i += 1
        return search_data


    def get_mange_info(self, url):
        """Gets the manga info from a url.

        Args:
            url (str): URL of the manga.

        Returns:
            dict: Returns a dict containing the manga's info.
        """
        info_data = {}
        rsp = scraper.get(url).text
        soup = BeautifulSoup(rsp, 'lxml')
        cover = soup.find("div", attrs={"class":"story-info-left"}).find("img")['src']
        plot = soup.find('div', attrs={"class":"panel-story-info-description"}).text[15:].replace("<br>", "").replace("Summary:", "")[2:]
        info_block = soup.find("div", attrs={"class":"story-info-right"})
        title = info_block.find("h1").text
        
        main_table = info_block.find("table", attrs={'class':'variations-tableInfo'}).find_all("tr")
        info_data = {
            "Title": title,
            "Plot": plot if "MangaNato.com" not in plot else "",
            "Cover": cover
        }
        info_data['Genre'] = [gen.text for gen in main_table[-1].find("td", attrs={"class":"table-value"}).find_all("a", attrs={"class":"a-h"})]
        # for only chapter (with name) no. ------> li.find("a").text[8:]
        # [['chapeter no. with name', 'link','date'], .......]
        
        info_data['Chapters'] = [[li.find("a").text, li.find("a")['href'], li.find("span", attrs={"class":"chapter-time text-nowrap"}).text] for li in soup.find("div", attrs={"class":'panel-story-chapter-list'}).find("ul", attrs={"class":"row-content-chapter"}).find_all("li", attrs={"class":"a-h"})]
        z = main_table.pop(-1)
        try:
            alternative_name = main_table[0].find("h2").text.split(" ; ")
            info_data["Alternative_names"] = alternative_name
        except (AttributeError, IndexError):
            pass
        try:
            authors = main_table[1].find("a", attrs={"class":"a-h"}).text.split(", ")
            info_data['Authors'] = authors
        except (AttributeError, IndexError):
            pass
        try:
            status = main_table[2].find("td", attrs={"class":"table-value"}).text
            info_data['Status'] = status
        except (AttributeError, IndexError):
            pass
        return info_data
    
    
    def download_chapter(self, url, path):
        """Download a particular chapter of a manga.

        Args:
            url (str): Chapter url.
            path (str): Path to the folder to download.
        """
        img_urls = self.get_chapter_images(url)
        response = scraper.get(url).text
        soup = BeautifulSoup(response, 'lxml')
        a_lst = soup.find("div", attrs={"class": "panel-breadcrumb"}).find_all("a", attrs={"class":"a-h"})
        title = a_lst[1].text.replace(":", "").replace("?", "").replace("<", "").replace(">","").replace("|", "")
        chapter = a_lst[2].text.strip()
        if os.path.exists(path) and os.path.exists(os.path.join(path, title)):
            # Folder with title name already exists
            if not os.path.exists(os.path.join(path, title, chapter)):
                os.mkdir(os.path.join(path, title, chapter))
        else:
            os.mkdir(os.path.join(path, title))
            os.mkdir(os.path.join(path, title, chapter))
        
        print(f"Downloading {len(img_urls)} images!")
        for i, img in enumerate(img_urls):
            cont = requests.get(img, headers=self.header).content
            with open(f"{os.path.join(path, title, chapter, str(i + 1))}.png", 'wb') as file:
                file.write(cont)
        print("Finished!")
        
    
    def download_manga(self, url: str, path: str):
        """Download all the chapters for a manga

        Args:
            url (str): URL for the manga
            path (str): Path to download folder
        """
        response = scraper.get(url).text
        soup = BeautifulSoup(response, 'lxml')
        info_block = soup.find("div", attrs={"class":"story-info-right"})
        title = info_block.find("h1").text.replace(":", "").replace("?", "").replace("<", "").replace(">","").replace("|", "")
        chapters = [[li.find("a").text, li.find("a")['href']] for li in soup.find("div", attrs={"class":'panel-story-chapter-list'}).find("ul", attrs={"class":"row-content-chapter"}).find_all("li", attrs={"class":"a-h"})]
        print(title, f"Total Chapters: {len(chapters)}",sep="\n")
        for i, chap in enumerate(chapters[::-1]):
            chapter = chap[0].replace(":", "").replace("?", "").replace("<", "").replace(">","").replace("|", "")
            c_url = chap[1]
            c_imgs = self.get_chapter_images(c_url)
            if os.path.exists(path) and os.path.exists(os.path.join(path, title)):
            # Folder with title name already exists
                if not os.path.exists(os.path.join(path, title, chapter)):
                    os.mkdir(os.path.join(path, title, chapter))
            else:
                os.mkdir(os.path.join(path, title))
                os.mkdir(os.path.join(path, title, chapter))
            print(f"    Downloading Chapter {i + 1}")
            for i, img in enumerate(c_imgs):
                cont = requests.get(img, headers=self.header).content
                with open(f"{os.path.join(path, title, chapter, str(i + 1))}.png", 'wb') as file:
                    file.write(cont)
            print("    Finished!")
    
        
    def get_genre_list(self, url, page_limit: int = 1) -> dict:
        """Gets a list of manga from a genre url.

        Args:
            url (str): Genre URL.
            page_limit (int, optional): No. of pages to get results from. Defaults to 1.

        Returns:
            dict: Returns a dict containing multiple dicts
        """
        genre_data = {}
        n = 1
        for i in range(1, page_limit + 1):
            res = scraper.get(f"{url}{str(i)}").text
            soup = BeautifulSoup(res, 'lxml')
            cont = soup.find("div", attrs={"class": "truyen-list"}).find_all("div", attrs={'class':"list-truyen-item-wrap"})
            for div in cont:
                nsoup = BeautifulSoup(str(div), 'lxml')
                img = nsoup.find("img")['src']
                #nsoup = nsoup.find("div", attrs={"class": "genres-item-info"})
                title = nsoup.find("h3").find("a").text
                url = nsoup.find("h3").find('a')['href']
                chapter = nsoup.find_all("a")[1].text
                genre_data[str(n)] = {
                    "Title": title,
                    "Cover": img,
                    "Url": url,
                    "Latest_Chapter": chapter
                }
                n += 1
        return genre_data
        

    def get_chapter_images(self, url):
        """Gets the list of all images for a particular manga chapter.

        Args:
            url (str): URL of the manga's chapter.

        Returns:
            list: Returns a list of url of the images.
        """
        rs = scraper.get(url).text
        soup = BeautifulSoup(rs, 'lxml')
        img_cont = soup.find("div", attrs={"class": "container-chapter-reader"}).find_all("img")
        img_links = [img['src'] for img in img_cont]
        return img_links
        
        
    def __load_genres(self):
        with open("genre.json", 'r') as file:
            self.genres = json.load(file).get("Mangakakalot")
    
import json
import cloudscraper
from bs4 import BeautifulSoup
from manganato import MangaNato

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


    def get_manga_info(self, url):
        """Gets the manga info from a url.

        Args:
            url (str): URL of the manga.

        Returns:
            dict: Returns a dict containing the manga's info.
        """
        info_data = {}
        rsp = scraper.get(url).text
        soup = BeautifulSoup(rsp, 'lxml')
        cover = soup.find("div", attrs={"class":"manga-info-pic"}).find("img")['src']
        plot = soup.find('div', attrs={"id":"noidungm"}).text[15:].replace("<br>", "").replace("Summary:", "")[2:]
        info_block = soup.find("ul", attrs={"class":"manga-info-text"})
        title = info_block.find("h1").text
        
        main_table = info_block.find_all("li")
        info_data = {
            "Title": title,
            "Plot": plot if "MangaNato.com" not in plot or "Mangakakalot.com" not in plot else "",
            "Cover": cover
        }
        if "Genre" in main_table[-4].text:
            info_data['Genre'] = [gen.text for gen in main_table[-4].find_all("a")]
        else:
            for li in main_table:
                if "Genre" in li.text:
                    info_data['Genre'] = [gen.text for gen in li.find_all("a")]
        #info_data['Genre'] = [gen.text for gen in info_block[-4].find_all("a") if "Genre" info_block[-4].text]
        # for only chapter (with name) no. ------> li.find("a").text[8:]
        # [['chapeter no. with name', 'link','date'], .......]
        
        info_data['Chapters'] = [[li.find("a").text, li.find("a")['href'], li.find_all("span")[-1].text] for li in soup.find("div", attrs={"class":'manga-info-chapter'}).find("div", attrs={"class":"chapter-list"}).find_all("div", attrs={"class":"row"})]
        alternative_name = info_block.find("h2").text.replace("Alternative : ", "").split(" ; ")
        info_data["Alternative_names"] = alternative_name
        
        if "Author" in main_table[1].text:
            authors = [i.text for i in main_table[1].find_all("a")]
        else:
            for li in main_table:
                if "Author" in li.text:
                    authors = [i.text for i in li.find_all("a")]
        info_data['Authors'] = authors
        
        status = main_table[2].text.replace("Status : ", "") if "Status" in main_table[2].text else "Updating"
        info_data['Status'] = status
        return info_data
        
    
    def get_manga_chapters(self, url: str):
        """Get imgs url for all the chapters for a manga.

        Args:
            url (str): URL for the manga
            path (str): Path to download folder
        
        Returns:
            tuple: Returns a tulpe containing dict and str
        """
        all_chap = {}
        response = scraper.get(url).text
        soup = BeautifulSoup(response, 'lxml')
        info_block = soup.find("ul", attrs={"class":"manga-info-text"})
        title = info_block.find("h1").text#.replace(":", "").replace("?", "").replace("<", "").replace(">","").replace("|", "")
        chapters = [[li.find("a").text, li.find("a")['href']] for li in soup.find("div", attrs={"class":'manga-info-chapter'}).find("div", attrs={"class":"chapter-list"}).find_all("div", attrs={"class":"row"})]
        for i, chap in enumerate(chapters[::-1]):
            chapter = chap[0]#.replace(":", "").replace("?", "").replace("<", "").replace(">","").replace("|", "")
            c_url = chap[1]
            if "manganato" in c_url:
                c_imgs = MangaNato().get_chapter_images(c_url)
            c_imgs = self.get_chapter_images(c_url)
            all_chap[str(i + 1)] = {
                "Name": chapter,
                "Urls": c_imgs
            }
        return (all_chap, title)
            
    
        
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
    
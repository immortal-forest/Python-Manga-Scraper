# Python-Manga-Scraper-API

### Some manga scrapers that use web scraping to get manga data from different sites.

<br>

## API &rarr; [Manga-Scraper-API](https://manga-scraper-api.pgamer.repl.co)

<br>

## Available sites:

 - [Manganato](https://manganato.com/)
 - [Mangakakalot](https://mangakakalot.com/)

<br>

## APIs:
<ul>

<li>
<h3>/recent</h3>

    Methods: GET
    Args: 
        limit = no. of pages
        site = from Available sites (lower case)
    
    Response:
        [
            {
                "Cover": "...",
                "Latest_Chapter": "...",
                "Title": "...",
                "Url": "...",
                "id": ...
            },
            ...
        ]

</li>

<li>
<h3>/info</h3>

    Methods: GET, POST
    For GET:
        Args:
            url = manga url
            site = site name (lower case)
    For POST:
        Post data:
            data = {
                "url": "",
                "site": ""
            }
    
    Response:
        {
            "Alternative_names": [], 
            "Authors": [], 
            "Chapters": [
                [
                "chapter name", 
                "chapter url", 
                "date"
                ],
                ...
            ], 
            "Cover": "", 
            "Genre": [], 
            "Plot": "", 
            "Status": "", 
            "Title": ""
        }
 
 Note: Some values might not be in the response. This usually happens if the site hasn't added or updated the respective values for a particular manga.

</li>

<li>
<h3>/genre-link</h3>

    Methods: POST
    Post data:
        data = {
            "site": "",
            "genre": {genre name},
            "state": "",
            "type": ""
        }
    Response:
        {
            "Link: ""
        }
        *will be "Error!" if genre doesn't exists.

Note: state & type only in some sites. For more info see [genre](/genre.json) file

</li>

<li>
<h3>/genre-list</h3>

    Methods: GET, POST
    For GET:
        Args:
            limit = no. of pages
            url = genre url
            site = site name (lower case)
    For POST:
        Post data:
            data = {
                "limit": "",
                "url": "",
                "site": "",
            }
    Response:
        {
            "1": {
                "Cover": "...",
                "Latest_Chapter": "...",
                "Title": "...",
                "Url": "..."
            },
            ...
        }

</li>

<li>
<h3>/chapter-imgs</h3>

    Methods: GET, POST
    For GET:
        Args:
            url = chapter url
            site = site name
    For POST:
        Post data:
            data = {
                "url": "",
                "site": ""
            }
    Response:
        {
            "Urls": []
        }

</li>

<li>
<h3>/manga-chapters</h3>

    Methods: GET, POST
    For GET:
        Args:
            url = manga url
            site = site name
    For POST:
        Post data:
            data = {
                "url": "",
                "site": ""
            }
    Response:
        {
            "Title": "",
            "Chapters": {
                "1": {
                    "Name": "",
                    "Urls": []
                },
                ...
            }
        }

</li>

<li>
<h3>/search</h3>

    Methods: GET, POST
    For GET:
        Args:
            name = manga name
            limit = no. of pages
            site = site name
    For POST:
        Post data:
            data = {
                "name": "",
                "limit": ""
                "site": ""
            }
    Response:
        [
            {
                "Cover": "...",
                "Latest_Chapter": "...",
                "Title": "...",
                "Url": "...",
                "id": ...
            },
            ...
        ]

</li>


</ul>
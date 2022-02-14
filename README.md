# Meme Crawler

This script scrapes memes from a chosen category on imgflip.com.

## Requirements

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install following packages.

```bash
$ pip install requests
$ pip install beautifulsoup4
$ pip install lxml
```

## Usage
Firstly, go to the meme you want to scrape on imgflip and sort as you wish (e.g. Top 1 year, enable/disable "NSFW memes" etc.).

Secondly, scrape the pages you wish with the "base link" and safe to prefered file. Eg.:
1) scrape pages 18-20, safe to csv.
```python
$ python3 meme_crawler.py --source https://imgflip.com/meme/But-Thats-None-Of-My-Business?sort=top-365d  --first_page 18 --last_page 20 --write_to_csv
```
2) scrape pages 1-4, save to json.
```python
$ python3 meme_crawler.py --source https://imgflip.com/meme/But-Thats-None-Of-My-Business?sort=top-365d  --last_page 4 --write_to_json
```
4) scrape pages 1-10, print to terminal.
```python
$ python3 meme_crawler.py --source https://imgflip.com/meme/But-Thats-None-Of-My-Business?sort=top-365d  --first_page 1 --last_page 10
```
5) Save the scraped images from pages 1-3:
```python
$ python3 meme_crawler.py --source https://imgflip.com/meme/But-Thats-None-Of-My-Business?sort=top-365d  --last_page 3 --save_images
```
If the output was saved as a csv, open in the following way in excel: 
Daten > Externe Daten abrufen > Aus Text
Choose csv-file > Daten importieren > Mit Trenzeichen versehen > Weiter (check Tabstopp) > Fertigstellen


## License
[MIT](https://choosealicense.com/licenses/mit/)
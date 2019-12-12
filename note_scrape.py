import requests
import time
from bs4 import BeautifulSoup

import csv
import sys

from openpyxl import load_workbook

def map_category(path):
    book = load_workbook(r"cat/cat.xlsx")
    sheet = book ["Report"]

    A = sheet["A"]
    B = sheet["B"]

    path = path.replace("+", " ").lower()
    path = path.split(" ")

    for x in range(len(A)):
        stewie = str(A[x].value).replace("->", " ").lower()
        if path[0].lower() in stewie and path[1].lower() in stewie:
            #new = open("new_cat.txt", "a")
            return str(B[x].value)
            #new.write(f"{B[x].value.encode(sys.stdout.encoding, errors='replace')}")

def create_csv(csvData):
    with open('data.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(csvData)

    csvFile.close()

srcs = []

from tqdm import tqdm

def find_srcs(hrefs):

    i=0

    for h in hrefs:

        for i in range(1, 62):

            try:
                url = str(h).replace("[", "").replace("]", "").replace("'", "") + f"/page/{i}"  
                res = requests.get(url)
                soup = BeautifulSoup(res.text, "html.parser")

                a = soup.find_all("a", attrs={"class" : "listing_product_title"})

                for z in a:

                    src = []
                    src.append(z["href"])
                    srcs.append(src)

            except Exception as e:
                print(f"{e}\\1")
                pass

from multiprocessing import Process
from multiprocessing.dummy import Pool as ThreadPool

hrefs = [
    ["https://www.notebooksbilliger.de/notebooks"], ["https://www.notebooksbilliger.de/tablets"], ["https://www.notebooksbilliger.de/pc+systeme"], ["https://www.notebooksbilliger.de/gaming"], ["https://www.notebooksbilliger.de/tft+monitore"], ["https://www.notebooksbilliger.de/pc+hardware"], ["https://www.notebooksbilliger.de/drucker"], ["https://www.notebooksbilliger.de/netzwerk"], ["https://www.notebooksbilliger.de/beamer"], ["https://www.notebooksbilliger.de/server+thinclients+usv"]
]

pool = ThreadPool(16)
pool.map(find_srcs, hrefs)

def get_data(srcs):

    for s in tqdm(srcs):

        try:

            f = open("data.txt", "a")

            url = str(s).replace("[", "").replace("]", "").replace("'", "")
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            
            try:
                price = soup.findAll("span", attrs={"class": "product-price__regular"})
                price = price[len(price) - 1].text.strip()

                price = price.replace("€", "").replace(" ", "").replace(".", "").replace(",", ".")

                if float(price) <=63:
                    l = float(price) * 9.88
                if float(price) > 63 and float(price) < 153:
                    l = float(price) * 9.49
                if float(price) > 153 and float(price) < 400:
                    l = float(price) * 9.09
                if float(price) > 400:
                    l = float(price) * 8.7

                price = l

            except:
                price = soup.findAll("span", attrs={"class": "product-price__regular"})
                price = price[len(price) - 1].text.strip()

            title = soup.find(
                "h1", attrs={"class": "name squeezed"}).text.strip()

            if "B-Ware" in title:
                continue

            #des = []

            description = soup.find(
                "table", attrs={"class": "properties_table"})
            desc = str(description).encode(sys.stdout.encoding, errors='replace')

            imgs = soup.find_all(
                "img", attrs={"class": "lbThumb"})

            imgs_links = []

            for img in imgs:
                imgs_links.append(img["src"].replace("?size=50", "").replace("?size=400", ""))
            imgs_linkss = ", ".join(imgs_links)

            #path = soup.find(
            #   "div", attrs={"id": "path_text"}).text.replace("\n", "").replace(" ", "").replace("\xa0", "").replace("Startseite", "").strip()

            p = s.split("/")
            path = p[3] + " " + p[4].replace("+", " ")
            path = map_category(path)

            article_num = soup.find(
                "div", attrs={"class": "article_number"}).text.replace("Artikelnummer:", "").replace(" ", "").replace("A", "").strip()

            f.write(f"{title}\t{price}\t{str(desc)}\t{article_num}\t{path}\t{imgs_linkss}\n")

            f.close()

            #csvData = [[title, price, str(desc), article_num, path, imgs_linkss]]
            #create_csv(csvData)

        except Exception as e:
            #print(f"{e}\\2")
            continue

#get_data()
pool.map(get_data, srcs)
pool.close()
pool.join()

import os
os.system("PAUSE > nul")
import requests
import bs4
from bs4 import BeautifulSoup
from enum import Enum
import pandas as pd
import mcws_common

url = "https://minecraft.wiki/w/Java_Edition_version_history"


def scrape_section(url):
    resp = requests.get(url)
    print(resp.status_code)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup
    
# def dump(obj:bs4.Tag):
#     # with open("output.html", "w", encoding="utf-8") as f:
#     #     f.write(obj.prettify())
#     with open("dump.html", "a", encoding="utf-8") as f:
#         f.write(obj.prettify())  # or table, or soup, etc.
#         f.write("\n")
        
#this function is not very good
def is_wikitable_with_1x(tag):
    return (
        tag.name == "table" and
        "wikitable" in tag.get("class", []) and
        tag.has_attr("data-description") and
        tag["data-description"].startswith("1.")
    )
    
class VersionStage(Enum):
    PRECLASSIC = -6
    CLASSIC = -5
    INDEV = -4
    INFDEV = -3
    ALPHA = -2
    BETA = -1
    RELEASE = 1
    
# NOTE: all pre-alpha versions will only be ordered by "major" version.  
class VersionObj:
    def __init__(self,major:int = 0,minor:int = 0, patch:int = 0, extension = "",stage:VersionStage=VersionStage.RELEASE,):
        self.stage:VersionStage = stage
        self.major:int = major
        self.minor:int = minor
        self.patch:int = patch
        self.extension = extension
    
    def __str__(self) -> str:
        return  str(self.stage.name)+" "+ ".".join(map(str,[self.major,self.minor,self.patch]))+self.extension
    def __repr__(self) -> str:
        return  str(self.stage.name)+" "+ ".".join(map(str,[self.major,self.minor,self.patch]))+self.extension


def fetch_release_versions(page:bs4.Tag)->list[VersionObj]:
    ret = []
    tables = page.find_all(is_wikitable_with_1x)
    
    
    
    #fetch release versions
    wikitables = page.select('table.wikitable[data-description^="1."]')
    for table in wikitables:
        dump(table)
    for table_idx, table in enumerate(wikitables, start=1):
        print(f"\nTable {table_idx}:")

        # Loop through rows
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                second_cell = cells[1]
                
                a_tag:bs4.Tag = second_cell.find("a", href=True)
                if a_tag:
                    ver_info = a_tag.text.split(".")
                    version = VersionObj(*ver_info)
                    ret.append(version)
                    
                    # print(a_tag['href'])  # href can be relative (e.g. /wiki/Stone)
        # print(type(wikitables), len(wikitables))
    return ret
        
        
# test works 
if __name__ == "__main__":
    version_list:list[VersionObj] = []
    wiki_html = mcws_common.html_getter.get_wiki_html("Java_Edition_version_history")
    bwiki_html = BeautifulSoup(wiki_html,"html.parser")
    
    start = bwiki_html.find(id='Full_release')
    end = bwiki_html.find(id='References')
    assert start is not None
    current = start.find_next()
    elements_between = []
    while current and current != end:
        # print(current)
        elements_between.append(current)
        current = current.next_element
    print(len(elements_between))
    # for i in elements_between:
    #     print(f"{i=}")
    
    wikitables = [el for el in elements_between if el.name == "table" and "wikitable" in el.get("class", [])]
    
    # print(wikitables[0], type(wikitables[0]))
    
    # for i in wikitables:
    #     mcws_common.common.dump(i)
    
    for i in wikitables:
        a,b,c,d = mcws_common.wikitable_parser.pre_process_table(i)
        out = mcws_common.wikitable_parser.process_rows(a,b,c,d)
        if d != "Key":
            print(f"{out}")

    # page = scrape_section(url)
    # print()
    # print(fetch_release_versions(page))
    
    # page.find()
    # element = page.find(id="Full_release")
    # dump(element)
    

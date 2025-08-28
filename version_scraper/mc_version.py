import requests
import bs4
from bs4 import BeautifulSoup
from enum import IntEnum
import pandas as pd
import mcws_common
import numpy as np
import re
from dateutil import parser
from typing import Optional
import datetime

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
    
class VersionStage(IntEnum):
    PRECLASSIC = -6
    CLASSIC = -5
    INDEV = -4
    INFDEV = -3
    ALPHA = -2
    BETA = -1
    RELEASE = 1
    
# NOTE: all pre-alpha versions will only be ordered by "major" version.  
class VersionObj:
    def __init__(self,major:int = 0,minor:int = 0, patch:int = 0, extension = 0,stage:VersionStage=VersionStage.RELEASE,release_date:Optional[datetime.datetime]=None, name = ""):
        self.major:int = major
        self.minor:int = minor
        self.patch:int = patch
        self.extension:int = extension
        self.stage:VersionStage = stage
        self.name = name
        self.release_date = release_date
        if self.name == "":
            self.name = self.fnstring()
        else:
            self.name = name

    def fnstring(self):
        if self.extension:
            return  str(self.stage.name)+" "+ ".".join(map(str,[self.major,self.minor,self.patch]))+"_"+str(self.extension)
        else:
            return  str(self.stage.name)+" "+ ".".join(map(str,[self.major,self.minor,self.patch]))
    
    def __str__(self) -> str:
        return self.fnstring()
    def __repr__(self) -> str:
        return self.fnstring()
    def __lt__(self, other):
        return (self.stage,self.major, self.minor, self.patch,self.extension) < (other.stage,other.major, other.minor, other.patch,other.extension)


# tested 8-27-2025
def fetch_release_versions(bwiki_html:bs4.Tag)->list[VersionObj]:
    stage = VersionStage(1)
    start = bwiki_html.find(id='Full_release')
    end = bwiki_html.find(id='Beta')
    version_name_column = 1
    release_date_column = 3
    
    
    tables:list[pd.DataFrame] = []
    release_versions:list[VersionObj]=[]

    assert start is not None
    assert end is not None
    
    current = start.find_next()
    elements_between = []
    while current and current != end:
        # print(current)
        elements_between.append(current)
        current = current.next_element
        
    wikitables = [el for el in elements_between if el.name == "table" and "wikitable" in el.get("class", [])]

    for i in wikitables:
        a,b,c,d = mcws_common.wikitable_parser.pre_process_table(i)
        out = mcws_common.wikitable_parser.process_rows(a,b,c,d)
        out = mcws_common.wikitable_parser.set_first_row_as_header(out)
        if d != "Key":
            tables.append(out)
            
    
    
    for table in tables:
        for version,release_date in zip(table.iloc[:,version_name_column],table.iloc[:,release_date_column]):
            
                
            if pd.isna(version):
                # print("nan value")
                continue
            try:
                # print(version,type(release_date),f"{release_date=}")
                parsed_date = parser.parse(release_date)
            except parser.ParserError:
                parsed_date = None
            try:
                # print(version,type(release_date),f"{release_date=}")
                
                parsed_date = parser.parse(release_date)
            except parser.ParserError:
                parsed_date = None
            except TypeError:
                if not pd.notna(release_date):
                    parsed_date = None
                else:
                    raise Exception("youre fucked")
            assert isinstance(version,str)
            split_version = version.split('.')
            if len(split_version)==2:
                split_version.append("0")
            major,minor,patch = map(int,split_version)
            release_versions.append(VersionObj(major,minor,patch,stage=stage,release_date=parsed_date))
    
    for version in release_versions:
        print(version,version.release_date)
    return release_versions
    #     print(i)
    # print(tables[0],tables[0].iloc[:,1])
    
def fetch_beta_versions(bwiki_html:bs4.Tag)->list[VersionObj]:
    stage = VersionStage(-1)
    prefix = "Beta "
    suffixes:list[str] = [" (Server only)"]
    end = bwiki_html.find(id='Alpha')
    start = bwiki_html.find(id='Beta')
    version_name_column = 1
    release_date_column = 3
    
    tables:list[pd.DataFrame] = []
    beta_versions:list[VersionObj]=[]

    assert start is not None
    assert end is not None
    
    current = start.find_next()
    elements_between = []
    while current and current != end:
        # print(current)
        elements_between.append(current)
        current = current.next_element
        
    wikitables = [el for el in elements_between if el.name == "table" and "wikitable" in el.get("class", [])]

    for i in wikitables:
        a,b,c,d = mcws_common.wikitable_parser.pre_process_table(i)
        out = mcws_common.wikitable_parser.process_rows(a,b,c,d)
        out = mcws_common.wikitable_parser.set_first_row_as_header(out)
        if d != "Key":
            tables.append(out)
            
    
    
    for table in tables:
        for version,release_date in zip(table.iloc[:,version_name_column],table.iloc[:,release_date_column]):            
                
            if pd.isna(version):
                # print("nan value")
                continue
            try:
                # print(version,type(release_date),f"{release_date=}")
                
                parsed_date = parser.parse(release_date)
            except parser.ParserError:
                parsed_date = None
            except TypeError:
                if not pd.notna(release_date):
                    parsed_date = None
                else:
                    raise Exception("youre fucked")
            assert isinstance(version,str)
            split_version = version.split('.')
            
            
            split_version[0] = split_version[0].removeprefix(prefix)
            for suffix in suffixes:
                split_version[-1] = split_version[-1].removesuffix(suffix)
            
            if len(split_version)==2:
                split_version.append("0")
            
            # check for extension to version
            # what the fuck bro
            extension_check = split_version[1].split("_")
            extension = ""
            if len(extension_check)==2:
                split_version[1]=extension_check[0]
                extension = extension_check[1]
            else : extension=0
            
            
            
            major,minor,patch = map(int,split_version)
            beta_versions.append(VersionObj(major,minor,patch,extension=int(extension),stage=stage))
    
    for version in beta_versions:
        print(version)
    #     print(i)
    # print(tables[0],tables[0].iloc[:,1])
    return beta_versions

def remove_suffix_parens(s):
    # Remove last parentheses and anything inside them, including the parentheses
    return re.sub(r'\s*\([^)]*\)\s*$', '', s)

def fetch_alpha_versions(bwiki_html:bs4.Tag)->list[VersionObj]:
    stage = VersionStage(-2)
    prefix = "Alpha v"
    suffixes:list[str] = [" (Server only)"," (Halloween Update)"," (Seecret Saturday 1)"," (Seecret Friday 9)"]
    start = bwiki_html.find(id='Alpha')
    end = bwiki_html.find(id='Infdev')
    version_name_column = 1
    release_date_column = 3    
    
    tables:list[pd.DataFrame] = []
    alpha_versions:list[VersionObj]=[]

    assert start is not None
    assert end is not None
    
    current = start.find_next()
    elements_between = []
    while current and current != end:
        # print(current)
        elements_between.append(current)
        current = current.next_element
        
    wikitables = [el for el in elements_between if el.name == "table" and "wikitable" in el.get("class", [])]

    for i in wikitables:
        a,b,c,d = mcws_common.wikitable_parser.pre_process_table(i)
        out = mcws_common.wikitable_parser.process_rows(a,b,c,d)
        out = mcws_common.wikitable_parser.set_first_row_as_header(out)
        if d != "Key":
            tables.append(out)
            
    
    
    for table in tables:
        
        for version,release_date in zip(table.iloc[:,version_name_column],table.iloc[:,release_date_column]):            
            
                
            if pd.isna(version):
                # print("nan value")
                continue
            try:
                # print(version,type(release_date),f"{release_date=}")
                
                parsed_date = parser.parse(release_date)
            except parser.ParserError:
                parsed_date = None
            except TypeError:
                if not pd.notna(release_date):
                    parsed_date = None
                else:
                    raise Exception("youre fucked")
                
            assert isinstance(version,str)
            version = remove_suffix_parens(version)
            split_version = version.split('.')
            
            
            split_version[0] = split_version[0].removeprefix(prefix)
            # for suffix in suffixes:
            #     split_version[-1] = split_version[-1].removesuffix(suffix)
            
            if len(split_version)==2:
                split_version.append("0")
            
            # check for extension to version
            # what the fuck bro
            extension_check = split_version[2].split("_")
            extension = ""
            if len(extension_check)==2:
                split_version[2]=extension_check[0]
                extension = extension_check[1]
            else : extension=0
            
            
            
            major,minor,patch = map(int,split_version)
            alpha_versions.append(VersionObj(major,minor,patch,extension=int(extension),stage=stage))
    
    for version in alpha_versions:
        print(version)
    #     print(i)
    # print(tables[0],tables[0].iloc[:,1])
    return alpha_versions


# def fetch_infdev_versions(bwiki_html:bs4.Tag)->list[VersionObj]:
#     stage = VersionStage(-3)
#     prefix = "infdev"
#     end = bwiki_html.find(id='Indev')
#     start = bwiki_html.find(id='Infdev')
#     version_column = 0
    
    
#     tables:list[pd.DataFrame] = []
#     infdev_versions:list[VersionObj]=[]

#     assert start is not None
#     assert end is not None
    
#     current = start.find_next()
#     elements_between = []
#     while current and current != end:
#         # print(current)
#         elements_between.append(current)
#         current = current.next_element
        
#     wikitables = [el for el in elements_between if el.name == "table" and "wikitable" in el.get("class", [])]

#     for i in wikitables:
#         a,b,c,d = mcws_common.wikitable_parser.pre_process_table(i)
#         out = mcws_common.wikitable_parser.process_rows(a,b,c,d)
#         out = mcws_common.wikitable_parser.set_first_row_as_header(out)
#         if d != "Key":
#             tables.append(out)
    
    
#     #reverse order of updates
#     merged_tables:pd.DataFrame = pd.concat(tables,ignore_index=True)
    
#     merged_tables = merged_tables.iloc[::-1].reset_index(drop=True)
    
#     version_num = 0
#     for index,row in merged_tables.iterrows():
#         VersionObj(major = version_num,stage = stage,name = row.['Version/release date'])
#         version_num+=1
#         #table.iloc[:,version_column]

    
    
#     return infdev_versions



# test works 8-26-2025
def test():
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
    
if __name__ == "__main__":
    wiki_html = mcws_common.html_getter.get_wiki_html("Java_Edition_version_history")
    bwiki_html = BeautifulSoup(wiki_html,"html.parser")
    release = fetch_release_versions(bwiki_html)
    beta = fetch_beta_versions(bwiki_html)
    alpha = fetch_alpha_versions(bwiki_html)
    
    print(f"{release[0]<release[2]=}")
    print(f"{release[0]<beta[0]=}")
    print(release[0],release[2])
    print(release[0],beta[0])

import requests

def get_wiki_html(title:str):
    """returns wiki html

    Args:
        title (str): string after "/w/"

    Returns:
        _type_: html as str
    """
    endpoint = "https://minecraft.wiki/api.php"

    # https://minecraft.wiki/api.php?action=parse&format=json&title=Test&text=%7B%7BPAGENAME%7D%7D&formatversion=2
    # https://minecraft.wiki/api.php?action=parse&format=json&page=Project%3ASandbox&formatversion=2
    # response = requests.get("https://minecraft.wiki/api.php?action=parse&format=json&page=Java_Edition_version_history&prop=text")
    params = {
        "action": "parse",
        "format":"json",
        "prop": "text",
        "page": title,
        "formatversion":"2",
    }


    
    response = requests.get(endpoint,params=params)
    # print(response.url)
    # print(f"{response.text[:1000]=}")
    data = response.json()

    html:str = data["parse"]["text"]
    # dump
    
    return html

# text = get_wiki_html("Java_Edition_version_history")
# print(text[:1000])  # Preview first 1000 chars

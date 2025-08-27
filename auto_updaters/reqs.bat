call .\venv\scripts\activate
pipreqs src/mcws_common/mcws_common --force
pipreqs version_scraper --force
type auto_updaters\mcws_scraper.txt >> version_scraper\requirements.txt
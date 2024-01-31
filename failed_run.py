import subprocess
from sport_handlers.basketball_handler import Basketball
from sport_handlers.main_handler import MatchHandler


urls = [

"https://www.basketball24.com/south-korea/kbl",
"https://www.basketball24.com/switzerland/sb-league"


]


for url in urls:
    file_name = '-'.join(url.split('/')[-2:])
    print(file_name)
    with open(f"details\\txt_links\\failed\\{file_name}.txt", 'r') as file:
        links = [line.strip() for line in file.readlines()]
    basketball_handler = Basketball(links, url)
    basketball_handler.open_browser_and_process_links()
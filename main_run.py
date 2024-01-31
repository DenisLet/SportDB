import subprocess
from sport_handlers.basketball_handler import Basketball
from sport_handlers.main_handler import MatchHandler


urls = [

"https://www.basketball24.com/iceland/premier-league",

]


for url in urls:
    subprocess.run(['python', 'link_collector.py', url], check=True)
    file_name = '-'.join(url.split('/')[-2:])
    print(file_name)
    with open(f"details\\txt_links\\{file_name}.txt", 'r') as file:
        links = [line.strip() for line in file.readlines()]
    basketball_handler = Basketball(links, url)
    basketball_handler.open_browser_and_process_links()
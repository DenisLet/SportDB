text = "DENMARK: Basketligaen - Play Offs - Semi-finals"

result = text[text.find(":") + 1:].strip().split('-',1)[1].strip().upper()

print(result)

urls = 'https://www.basketball24.com/bulgaria/nbl'

print('-'.join(urls.split('/')[-2:]))



bb_home1q = 'smh__part  smh__home smh__part--1'
bb_home2q = 'smh__part  smh__home smh__part--2'
bb_home3q = 'smh__part  smh__home smh__part--3'
bb_home4q = 'smh__part  smh__home smh__part--4'
bb_home5q = 'smh__part  smh__home smh__part--5'
bb_away1q = 'smh__part  smh__away smh__part--1'
bb_away2q = 'smh__part  smh__away smh__part--2'
bb_away3q = 'smh__part  smh__away smh__part--3'
bb_away4q = 'smh__part  smh__away smh__part--4'
bb_away5q = 'smh__part  smh__away smh__part--5'



s1 = (4,5,6)
s2 = (1,2,3)

# print(sum(filter(lambda x: x is not None, s1)))
#
# s3 = [item for pair in zip(s1, s2) for item in pair]
print([None]*4)


lst = ['163.5\n1.30\n3.40', '166.5\n1.30\n3.40', '167\n1.8\n1.81', '167.5\n1.53\n2.33\n167.5\n1.32\n3.20', '168\n1.33\n3.10', '168.5\n1.57\n2.19\n168.5\n1.36\n3.00\n168.5\n1.53\n2.38', '169\n1.59\n2.16\n169\n1.38\n2.90', '169.5\n1.63\n2.11\n169.5\n1.41\n2.80', '170\n1.67\n2.08\n170\n1.43\n2.75', '170.5\n1.55\n2.23\n170.5\n1.46\n2.63', '171\n1.58\n2.17\n171\n1.48\n2.55', '171.5\n1.62\n2.13\n171.5\n1.52\n2.48\n171.5\n1.53\n2.38', '172\n1.58\n2.17\n172\n1.55\n2.43', '172.5\n1.61\n2.12\n172.5\n1.58\n2.33\n172.5\n1.84\n2.00', '173\n1.64\n2.09\n173\n1.61\n2.28', '173.5\n1.69\n2.04\n173.5\n1.65\n2.20', '174\n1.72\n2.02\n174\n1.68\n2.16', '174.5\n1.77\n1.98\n174.5\n1.73\n2.10', '175\n1.81\n1.95\n175\n1.76\n2.05', '175.5\n1.86\n1.92\n175.5\n1.81\n2.00', '176\n1.90\n1.89\n176\n1.85\n1.95', '176.5\n1.93\n1.85\n176.5\n1.90\n1.90\n176.5\n1.91\n1.91', '177\n1.96\n1.80\n177\n1.94\n1.86', '177.5\n2.00\n1.75\n177.5\n2.00\n1.82', '178\n2.03\n1.71\n178\n2.04\n1.77', '178.5\n2.07\n1.67\n178.5\n2.08\n1.73\n178.5\n2.50\n1.50', '179\n2.11\n1.63\n179\n2.15\n1.70', '179.5\n2.14\n1.60\n179.5\n2.20\n1.66', '180\n2.19\n1.57\n180\n2.28\n1.62', '180.5\n2.18\n1.59\n180.5\n2.32\n1.60', '181\n2.23\n1.55\n181\n2.40\n1.55', '181.5\n2.28\n1.53\n181.5\n2.45\n1.53\n181.5\n2.50\n1.50', '182\n2.55\n1.49', '182.5\n2.60\n1.47', '183\n2.70\n1.44', '183.5\n2.75\n1.42\n183.5\n3.40\n1.30', '184\n2.88\n1.40', '184.5\n2.95\n1.38', '185\n3.05\n1.35', '185.5\n1.1\n1.1', '186\n3.25\n1.30', '186.5\n3.35\n1.30\n186.5\n3.25\n1.33']
def find_average_total(coefline):
    k = None
    total = None
    min_diff = .9 # Инициализируем минимальное значение diff бесконечностью
    for case in coefline:
        current_total = case.split()[0]
        k1, k2 = list(map(float, case.split()[1:3]))
        diff = abs(k1 - k2)
        if diff < min_diff:
            min_diff = diff
            total = current_total
    print(f"The total with the smallest diff is: {total}")
    return total
find_average_total(lst)
print(float('inf'))

import os

# Путь к папке с текстовыми файлами
folder_path = './txt_links/failed'

# Список для хранения всех ссылок
all_links = []

# Проход по всем файлам в папке
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(folder_path, filename)

        # Открытие файла и добавление всех ссылок в список
        with open(file_path, 'r', encoding='utf-8') as file:
            links = file.read().splitlines()
            all_links.extend(links)

# Вывод списка всех ссылок
print(all_links)

scores_data = [None]*10
print(scores_data)
# urls = [ 'https://www.basketball24.com/france/lnb',
#          'https://www.basketball24.com/italy/lega-a',
#          'https://www.basketball24.com/germany/bbl',
#          'https://www.basketball24.com/spain/acb',
#          'https://www.basketball24.com/greece/basket-league',
#          'https://www.basketball24.com/turkey/super-lig',
#          'https://www.basketball24.com/russia/vtb-united-league'
#          ]
#
# urls = [
# "https://www.basketball24.com/austria/superliga",
# 'https://www.basketball24.com/russia/vtb-united-league',
# "https://www.basketball24.com/bulgaria/nbl",
#
#
#          ]


# urls= ['',
#        '"https://www.basketball24.com/denmark/basketligaen"',
#        '"https://www.basketball24.com/czech-republic/nbl"',
#           "https://www.basketball24.com/japan/b-league"
#        "https://www.basketball24.com/finland/korisliiga"
#
# ]


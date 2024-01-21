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
print(s1+s2)



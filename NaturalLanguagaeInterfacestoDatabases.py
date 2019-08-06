import pprint
import string
import sqlite3
import nltk
from nltk.parse import CoreNLPParser
from nltk.parse import CoreNLPDependencyParser
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk import load_parser
from nltk.tree import *

pos_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='pos')
ner_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')
parser = CoreNLPParser(url='http://localhost:9000')

def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)

grammarFile = open("newGrammar.fcfg","w+")

grammarFile.write("""## newGrammar.fcfg
## Modular string-based grammar for 
## deriving SQL queries from English
## 
## Authors: Ashish PVJS and Srikanth Maganti <vperur2@uic.edu and smagan20@uic.edu>\n""")

def createGrammar(query):
	parsetree = list(parser.raw_parse(query))
	Tree.fromstring(str(parsetree[0])).pretty_print()
	t = Tree.fromstring(str(parsetree[0]))
	productions = Tree.productions(t)
	cfgRHSList = []
	cfgLHSList = []
	worsdList = query.split()
	stopwords = ["'Is'","'Was'","'a'","'an'","'the'","'on'","'in'"]
	if worsdList[0] in ["Is","Was"]:
		# print('yay')
		for i in productions:
			s = str(i)
			# print(s)
			tempRuleList = s.split('->')
			rhsRule = ""
			lhsRule = ""
			ts = tempRuleList[1][1:-1]
			if tempRuleList[1].upper() == tempRuleList[1] and hasNumbers(str(ts))==False:
				if len(tempRuleList[1].split())!=1:
					# print("Hello")
					# print(tempRuleList[1].split())
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=("
				else:
					# print("Yello")
					# print(tempRuleList[1])
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM="
				lhslist = (tempRuleList[1].strip()).split()
				# print(lhslist)
				lhsRuleSet = set(lhslist)
				# print(lhsRuleSet)
				lhsRuleDict = {}
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						# print(k)
						lhsRuleDict[k]+=1
						rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"
				rhsRule = rhsRule[:-1]
				if len(tempRuleList[1].split())!=1:
					rhsRule = rhsRule + ")]"
				else:
					rhsRule = rhsRule + "]" 
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						# k = k.translate(str.maketrans('', '', string.punctuation))
						lhsRuleDict[k]+=1
						lhsRule = lhsRule+k.strip()+"[SEM=?"+k.lower()+str(lhsRuleDict[k])+"] "
				lhsRule = lhsRule[:-1]
			else:
				if tempRuleList[1].strip() in stopwords:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM='"+"']"
				else:
					rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + tempRuleList[1].strip() + "]"
				lhsRule = tempRuleList[1].strip()
			cfgRHSList.append(rhsRule)
			cfgLHSList.append(lhsRule)
		ans = ""
		for i in range(1,len(cfgRHSList)-1):
			s = cfgRHSList[i]+" -> "+cfgLHSList[i]+"\n"
			ans = ans+s
		start = ""
		for c in cfgRHSList[1]:
			if c!="[":
				start = start+c
			else:
				break
		return (start,ans)
	else:
		for i in productions:
			s = str(i)
			# print(s)
			tempRuleList = s.split('->')
			rhsRule = ""
			lhsRule = ""
			ts = tempRuleList[1][1:-1]
			if tempRuleList[1].upper() == tempRuleList[1] and hasNumbers(str(ts))==False:
				rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=("
				lhslist = (tempRuleList[1].strip()).split()
				# print(lhslist)
				lhsRuleSet = set(lhslist)
				# print(lhsRuleSet)
				lhsRuleDict = {}
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						# print(k)
						lhsRuleDict[k]+=1
						rhsRule = rhsRule+"?"+k.lower()+str(lhsRuleDict[k])+"+"
				rhsRule = rhsRule[:-1]
				rhsRule = rhsRule + ")]"
				for lrules in lhsRuleSet:
					lhsRuleDict[lrules]=0
				for k in lhslist:
					if k!='.':
						# k = k.translate(str.maketrans('', '', string.punctuation))
						lhsRuleDict[k]+=1
						lhsRule = lhsRule+k.strip()+"[SEM=?"+k.lower()+str(lhsRuleDict[k])+"] "
				lhsRule = lhsRule[:-1]
			else:
				rhsRule = rhsRule + tempRuleList[0].strip() + "[SEM=" + tempRuleList[1].strip() + "]"
				lhsRule = tempRuleList[1].strip()
			cfgRHSList.append(rhsRule)
			cfgLHSList.append(lhsRule)
		ans = ""
		for i in range(1,len(cfgRHSList)-1):
			s = cfgRHSList[i]+" -> "+cfgLHSList[i]+"\n"
			ans = ans+s
		start = ""
		for c in cfgRHSList[1]:
			if c!="[":
				start = start+c
			else:
				break
		return (start,ans)

# query = "Did PersonName direct MovieName?"

#nltk.data.show_cfg('samplegrammar.fcfg')

musicDBConn = sqlite3.connect('music.sqlite')
geographyDBConn = sqlite3.connect('WorldGeography.sqlite')
movieDBConn = sqlite3.connect('oscar-movie_imdb.sqlite')
musicDB = musicDBConn.cursor()
geographyDB = geographyDBConn.cursor()
movieDB = movieDBConn.cursor()
#query = "Did Neeson star in Schindler's List?"
# query = "Is Kubrick a director?"
# query = "Was Birdman the best movie in 2015?"
query = "Who directed Schindler's List?"
# query = "Who won the oscar for best actor in 2005?"
# query = "Which movie won the oscar in 2000?"
# query = "Who directed the best movie in 2010?"
# query = "Did Allen direct Mighty Aphrodite?"
finalquery = query
# queryNers = ner_tagger.tag((query.split()))
# for i in queryNers:
# 	if i[1]=="DATE":
# 		query = query.replace(i[0],"Date")
# print(query)

personName,movieName =[],[]
pos_tags=list(pos_tagger.tag(query.split()))
pos_tags.append(('last','$$$'))
print(pos_tags)
nnpTags,year = [],0
for i,k in enumerate(pos_tags):
	if pos_tags[i+1][1] == '$$$':
		break
	elif pos_tags[i][1]=='NNP' and pos_tags[i+1][1]!='NNP':
		nnpTags.append(pos_tags[i][0])
	elif pos_tags[i][1]=='NNP' and pos_tags[i+1][1]=='NNP':
		nnpTags.append(pos_tags[i+1][0])
	if pos_tags[i][1]=='CD':
		year=pos_tags[i][0]
print(nnpTags)

for i in nnpTags:
	temporaryqueryperson=("select name from person where name like '%{}%'").format(i)
	temporaryquerymovie=("select name from movie where name like '%{}%'").format(i)
	print(temporaryqueryperson)
	print(temporaryquerymovie)
	AlbumT1=movieDBConn.execute(temporaryqueryperson.upper())
	for row in AlbumT1:
			personName.append([row[0],0])
	AlbumT2=movieDBConn.execute(temporaryquerymovie.upper())
	for row in AlbumT2:
			movieName.append([row[0],0])

print("Personnames")
print(personName)
print("Movienames")
print(movieName)

for i in nnpTags:
	for k,x in enumerate(movieName):
		if (x[0].find(i))>=0:
			x[1]=x[1]+10
		else:
			x[1]=x[1]-1
	for j,y in enumerate(personName):
		if (y[0].find(i))>=0:
			y[1]=y[1]+10
		else:
			y[1]=y[1]-1

print("after Personnames")
print(personName)
print("after Movienames")
print(movieName)
finalmovienames,finalpersonnames,filteredmovienames=[],[],[]
for i in personName:
	if i[1]>0:
		finalpersonnames.append(i[0])
for i in movieName:
	if i[1]>0:
		finalmovienames.append(i[0])
print("final person")
print(finalpersonnames)
print("final movie")
for i in finalmovienames:
	if i.find(':')>=0:
		filteredmovienames.append(i.split(':')[0])
	else:
		filteredmovienames.append(i)
print(filteredmovienames)

if (finalpersonnames!=[]) and (filteredmovienames!=[]):
	for i in finalpersonnames:
		for k in nnpTags:
			if i.find(k)>=0:
				PersonName=k
				newquery=query.replace(k,'PersonName')
				break
	print("Given person name "+PersonName)
	for j in filteredmovienames:
		for l in nnpTags:
			if j.find(l)>=0:
				MovieName=j
				finalquery=newquery.replace(j,'MovieName')
	print("Given Movie Name "+MovieName)
elif (finalpersonnames!=[]) and (filteredmovienames==[]):
	for i in finalpersonnames:
		for k in nnpTags:
			if i.find(k)>=0:
				PersonName=k
				finalquery=query.replace(k,'PersonName')
				break
	print("Given person name "+PersonName)
elif (finalpersonnames==[]) and (filteredmovienames!=[]):
	for j in filteredmovienames:
		for l in nnpTags:
			if j.find(l)>=0:
				MovieName=j
				finalquery=query.replace(j,'MovieName')
	print("Given Movie Name "+MovieName)
print(finalquery)
start,grammar = createGrammar(finalquery)
grammarFile.write("%"+" start "+start+"\n")
grammarFile.write(grammar)
grammarFile.close()
# nerList = list(nerTagger.tag((finalquery.split())))
# for i in nerList:
# 	if i[1] == "DATE":
# 		year = i[0]
# 		finalquery = finalquery.replace(year,"year")
# 	if i[1] in ["CITY","STATE OR PROVINCE","LOCATION","COUNTRY"]:
# 		location = i[0]
# 		finalquery =finalquery.replace(location,"location")
# print(finalquery)
# print(location)

cp = load_parser("newGrammar.fcfg",trace=3)
trees = list(cp.parse(finalquery.strip('?').split()))
for tree in trees:
	print("\n")
	print(tree)
answer = trees[0].label()['SEM']
print(answer)
answer = [s for s in answer if s]
q = ' '.join(answer)
insertlambda=q
# for i in insertlambda:
# 	if i!="select":
# 		for i,k in enumerateinsertlambda:
# 			if k=='%s':
# 				insertlambda[k]=i
# print(insertlambda)
templist=[]
tlist = list(insertlambda.split(' '))
for words in tlist:
	if words!="select":
		print(1)
		templist.append(words)
	else:
		break

temp = insertlambda
# reverselist = list(temp.split(' '))[::-1]
reverselist = tlist[::-1]
for words in reverselist:
	if words!= ".":
		templist.append(words)
	else:
		break
print("templist")
print(templist)
tempstring = insertlambda.format(*templist)
print("in tempstring")
temporarystring=tempstring.split()
for i,k in enumerate(temporarystring):
	if k=="select":
		initial=i
	if k==".":
		end=i
print("initial value")
print(initial)
print("end value")
print(end)
finalstring=' '.join(temporarystring[initial:end])
print("finalstring")
print(finalstring.upper())
#AlbumT = movieDBConn.execute('''Select P.name FROM Person P
#INNER JOIN Oscar O ON P.id = person_id
#INNER JOIN Actor A ON A.actor_id = person_id
#WHERE P.pob LIKE "%Italy%" AND
#O.year = "1962"''')
#AlbumT = movieDBConn.execute(''' SELECT COUNT(*) FROM PERSON P 
#   INNER JOIN DIRECTOR D ON P.ID=D.DIRECTOR_ID 
#   INNER JOIN MOVIE M ON D.MOVIE_ID=M.ID 
#   WHERE P.NAME LIKE '%AllEN%' AND M.NAME LIKE "%APHRODITE%" ''')
# print("in database")
AlbumT=movieDBConn.execute(finalstring.upper())
for row in AlbumT:
    print(row)
musicDB.close()
geographyDB.close()
movieDB.close()


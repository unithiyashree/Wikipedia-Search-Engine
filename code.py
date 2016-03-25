import timeit
import sys
import re
import xml.sax.handler
from bs4 import BeautifulSoup
import collections
from collections import defaultdict
import zlib
import bz2
import Stemmer


''' Priority:
	0 : Title
	1 : Category
	2 : Links
	3 : Infobox
	4 : Body

	Output Format : word$doc_id#codecount$
'''

all_words = {}
stop_words = defaultdict( int)

# Dictionary for all the words
for i in range( 26):
	all_words[ str( unichr( ord( 'a') + i))] = defaultdict( dict)

# Dictionary for all the numbers
for i in range( 10):
	all_words[ str( i)] = defaultdict( dict)

index = {}
stemmer = Stemmer.Stemmer( 'english')


# Function to tokenize all the words in the sub-portions of the wiki-page
def tokenize( data):                                                 
  tokenizedWords = re.findall("\d+|[\w]+",data)
  tokenizedWords = [ key.encode('utf-8') for key in tokenizedWords]
  # print tokenizedWords
  return tokenizedWords

# Function to stem the words after tokenization
def stem(word):
	return str(stemmer.stemWord(word))
	#stemmer=SnowballStemmer('english')
	# return str(stemmer.stem(word))

# Function loads the stop words from a external file and then stores it as a list 
def get_stop_words():
	filename = open( 'stopwords.txt')
	data = filename.read()
	data = data.split('\n')
	for i in range( len( data) - 1):
		word = data[ i].strip()
		stop_words[ word] = 1
	return

# Function to get the category from the body of each document i.e page		
def get_category( data, doc_id):
	string = ""
	# Category = []
	#Reading each line to get the category attribute
	Lines = data.split('\n')
	# print str(len(Lines)) + " -- " + str(doc_id)
	for i in range( len( Lines) - 1): 
		if '[[Category:' in Lines[i]:
			Line = Lines[i].split( "[[Category:")
			if len( Line) > 1:
				# Category.extend( Line[ 1:-1])
				temp = Line[ -1].split(']]')
				string += temp[0]
				string += " "
	category_words = tokenize( string)
	# print category_words
	indexing( category_words, 1, doc_id)
	return

# Function to get the external links of each document i.e page
def get_externallinks( data, doc_id):
	imp_words =[]
	externallinks = data.split( "==External links==")
	if len( externallinks) == 1:
		return
	externallinks1 = externallinks[1].split( "\n\n")
	temp = externallinks1[0].split( "\n")
	for i in temp:
		externallinks_words = tokenize( i)
		indexing( externallinks_words, 2, doc_id)
	return

# Function to get the infobox data from the data of each document i.e page
def get_infobox( data, doc_id):
	infobox = data.split( "{{Infobox")
	if len( infobox)==1:
		return
	infobox1 = infobox[1].split( "}}")
	infobox_words = tokenize( infobox1[0])
	indexing( infobox_words, 3, doc_id)
	# infobox_words = tokenize( infobox1[0])
	return

#  Function to get the body data from each document i.e page
def get_body( data):
	body = data.find( 'text')
	body = (str(body).split('>'))[1]
	body = (str(body).split('<'))[0]
	# externallinks = get_externallinks( body)
	# print body
	return body

# Function to get the title of each document i.e page
def get_title( data):
 	title = data.find( 'title')
 	title = (str(title).split('>'))[1]
	title = (str(title).split('<'))[0]
	return title

# Function to get the doc_id which is helpful in mapping the words with documents while indexing
def get_doc_id( data):
	doc_id = data.find('id')
	doc_id = (str(doc_id).split('>'))[1]
	doc_id = (str(doc_id).split('<'))[0]
	return doc_id

# Function which creates indexes i.e, add details of each word occurences in dict of doc_id and the doc_id has to attributes
# 1) priority i.e, occurrence in which part of the document
# 2) total count
def indexing( tokens, priority, doc_id):
	for j in tokens:
		j = j.lower()
		if not stop_words[ j] == 1:
			j = stem( j)
			if j[ 0] not in all_words:
				continue
			if j in all_words[j[0]]:
				if doc_id in all_words[j[0]][j]:
					all_words[j[0]][j][doc_id] = [priority,all_words[j[0]][j][doc_id][1] + 1]
				else:
					all_words[j[0]][j][doc_id] = [ priority, 1]
			else:
				all_words[j[0]][j] = defaultdict( list)
				all_words[j[0]][j][doc_id] = [ priority, 1]

# Initial functions which gets the required data for indexing
def Input_parse():
	input_file = open( sys.argv[ 1])
	data = input_file.read()
	soup = BeautifulSoup( data, 'xml')
	document = soup.findAll( 'page')
	Numof_doc = len(document)
	# print Numof_doc
	for i in range( Numof_doc):
		title = get_title( document[i])
		doc_id = get_doc_id( document[i])
		body = get_body( document[i])
		indexing( tokenize( body), 4, doc_id)
		get_infobox( body, doc_id)
		get_externallinks( body, doc_id)
		get_category( body, doc_id)
		indexing( tokenize( title), 0, doc_id)

# Function to print the formed index in a compressed form in the output file
def output_index():
    filename = open(sys.argv[ 2], 'w')
    # testfile = open( 'nith.txt', 'w')
    # test_str = ''
    write_str = ''
    count = 0
    for letter in all_words:
		for word in all_words[ letter]:
			count = count + 1
			write_str = write_str + str(word) + '$'
			# test_str = test_str + str(word) + '$'
			for doc_id in all_words[letter][word]:
				write_str = write_str + str(doc_id) + '#' + str(all_words[letter][word][doc_id][0]) + '#' + str(all_words[letter][word][doc_id][1]) + '$'
				# test_str = test_str + str(doc_id) + '#' + str(all_words[letter][word][doc_id][0]) + '#' + str(all_words[letter][word][doc_id][1]) + '$'
			write_str = write_str + '\n'
			# test_str = test_str + '\n'
			# print write_str
			# testfile.write( test_str)
			test_str = ''
			if count == 1000:
				filename.write(bz2.compress(write_str,4))
				write_str = ''
				count = 0

# The code starts here.
if __name__ == "__main__":                                    
    start = timeit.default_timer()
    print 'Start'
    get_stop_words()
    Input_parse()
    stop1 = timeit.default_timer()
    print 'Data Processing time:' + str(stop1 - start)
    print 'Writing to Output file'
    output_index()
    	
    stop2 = timeit.default_timer()
    print 'total time :' + str( stop2 - start)
    print 'Stop'
  

		
	

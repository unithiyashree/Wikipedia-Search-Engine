WIKIPEDIA SEARCH ENGINE : Phase-1

Aim : To create index on wikipedia data dump of 100MB

LOGIC FOR CREATING THE INDEX:
The basic logic used to store the indexes is that a dictionary is created with 26 letters and possible 10 numbers. 
Each word is mapped according to the first letter into the respective dictionary and a dictonary is created for each corresponding word in the starting letter dictionary
The occurrence of each word in different doc_id is added to the corresponding word dictionary and doc_id dictionaries are created for each word accordingly.
The doc_id dictionary consists of 2 attributes
	1) The priority i.e, where in the document the occurence happens
	2) The total count of occurrences of the word

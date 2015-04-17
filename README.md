# SMPP
The Small Medical Phrase Parser - For named entity recognition (NER) in medical text.

# Introduction
The SMPP was originally created in Scala by an outstanding programmer, Sujit Pal (http://sujitpal.blogspot.com/). While using NER in an informatics experiment I found its performance for short sentences with a few concepts comparable OR BETTER than cTAKES, an industry standard medical NER program. I converted it to python and added a few features then wrapped it around the classic NegEx algorithm (https://code.google.com/p/negex/). I think you wil find its performance outstanding as well. 

# A possible use case
Short human-natural queries against a larger indexed corpus; for example, a human-friendly query system against a body of information tagged with UIMA/cTAKES and served up with Solr. 

# Setup
The SMPP requires that you have the UMLS installed locally. A good step-by-step set of instructions can be found on Sujit Pal's blog here (http://sujitpal.blogspot.com/2014/01/understanding-umls.html).

Once this is installed localy, log into your mysql and from the umls database you set up run:

mysql> select CUI, STR from MRCONSO 
...    where LAT = 'ENG' 
...    into outfile '/tmp/cuistr.csv' 
...    fields terminated by ',' 
...    enclosed by '"' lines 
...    terminated by '\n';
Query OK, 7871075 rows affected (23.30 sec)

Dedup items with same string and CUI:

$ cat cuistr.csv | sort | uniq > cuistr1.csv

Now from 

./SMPP/MedicalQueryParser/ 

edit 

medicalQueryParserBuildIndexTest.py

to reflect the location the cuistr1.csv is stored and where you want Lucene to build the index. 

...
mqp = MedicalQueryParser("./Data/UMLSIndex")
mqp.buildIndex("./Data/cuistr.csv")
...

This will take several hours. I have tested this on Mac and Ubuntu. On my Mac it does great, on my Ubunutu machine it will sometimes crash out of memory. I haven't had time to fix this and anyone is welcome to suggest an edit. This could have been stored in a database, there are a few reasons I chose not to switch it from Sujit's original construction. Make sure you have NLTK installed as the more aggressive Lancaster stemmer is dependent on this library.

Edit SimpleTage_MedicalQueryParser.py to reflect the location of the NegEx rule file. I've included it in this release so you shouldn't have to change anything here. 

# Testing

There are no unit tests, though there should be. There are simple wrappers around the core class MedicalQueryParser called medicalQueryParserTest.py that setup a small query line to play around with results. There is an analogous wrapper for SimpleTag in the root directory that returns the same results but with the SOFAs negation meta data included from the NegEx tie in. 

# Known issues
- Building the index on Ubuntu 

# Future additions
- Adding a less aggresive stemmer higher in the cascade before the more aggressive Lancaster stemmer so that results like image and imuran don't stem to the same result, or at least if they do it gets a lower score. 

Good luck!

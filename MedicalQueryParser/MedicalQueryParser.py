"""
The MIT License (MIT)

Copyright (c) 2015 John T Green, Sujit Pal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import string, nltk
from operator import itemgetter

from java.io import File 
from java.io import StringReader
#from java.util.concurrent.atomic.AtomicLong
#from java.util.regex.Pattern

#from scala.Array.canBuildFrom
#from scala.Array.fallbackCanBuildFrom
#from scala.collection.mutable.ArrayBuffer
#from scala.io.Source

from org.apache.lucene.analysis import Analyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute #?
from org.apache.lucene.analysis.tokenattributes import CharTermAttributeImpl
from org.apache.lucene.document import Document
from org.apache.lucene.document import Field
#from org.apache.lucene.document.Field import Index Access as methods
#from org.apache.lucene.document.Field import Store Access as methods
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.index import IndexReader
from org.apache.lucene.index import IndexWriter
from org.apache.lucene.index import IndexWriterConfig
from org.apache.lucene.index import Term
#from org.apache.lucene.search.BooleanClause import Occur
from org.apache.lucene.search import BooleanClause
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import IndexSearcher
#from org.apache.lucene.search import ScoreDoc
from org.apache.lucene.search import TermQuery
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

import re, string
from itertools import islice


class MedicalQueryParser:
    def __init__(self, luceneDir, includeAllResults=False, maxHits=10):
        self.luceneDir = luceneDir
        
        self.punctPattern = re.compile(r"\\p{Punct}")
        self.spacePattern = re.compile(r"\\s+")
        
        # Whether or not the cascade exits early, or collects everything
        self._includeAllResults = includeAllResults
        
        # Total hits returned per search... in this use case, this can be high.
        self._maxHits = maxHits
        
        # Stemmer setup
        self._stopWords = nltk.corpus.stopwords.words('english')
        self._stemmer = nltk.stem.lancaster.LancasterStemmer()
        
    def getDocument(self, reader, hit):
        doc = reader.document(hit.doc)
        
        return {
                    "id":doc.get("id"),
                    "cui":doc.get("cui"),
                    "str":doc.get("str"), 
                    "str_norm":doc.get("str_norm"),
                    "str_sorted":doc.get("str_sorted"), 
                    "str_stemmed":doc.get("str_stemmed"),
                    "str_stemmedSorted":doc.get("str_stemmedSorted")
                        
        }
    
    def normalizeCasePunct(self, stringToNormalize):
        tableTranslation = string.maketrans(string.punctuation, " "*len(string.punctuation))
        return filter(lambda x: x in string.printable,
                    " ".join(stringToNormalize.translate(tableTranslation).split()).lower()
                    )
        
    def sortWords(self, stringToSort):
        return " ".join(sorted(stringToSort.split(), key=lambda x: x[0]))
    
    def getAnalyzer(self): 
        return StandardAnalyzer(Version.LUCENE_CURRENT)

    def stemWords(self, stringToStem):            
        return " ".join(
            [self._stemmer.stem(word) for word in stringToStem.split() if word not in self._stopWords]
            )
    
    def alreadySeen(self, refset, ngram):
        words = ngram.split()
        nseen = len([word for word in words if word not in refset])
        
        if refset == []:
            return True
        elif nseen > 0:
            return True
        else:
            return False
    
    def window(self, seq, n=2):
        "Returns a sliding window (of width n) over data from the iterable"
        "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
        
        it = iter(seq)
        result = tuple(islice(it, n))
        if len(result) == n:
            yield result
        for elem in it:
            result = result[1:] + (elem,)
            yield result
    
    def annotateConcepts(self, phrase):
        suggestions = []
        
        reader = DirectoryReader.open(
            SimpleFSDirectory( File(self.luceneDir) )) 
    
        searcher = IndexSearcher(reader)
        
        # Try exact match
        suggestions = self.cascadeSearch(searcher, reader, phrase, 1.0)
        
        # No exact match, fall back to inexact
        if len(suggestions) == 0 or self._includeAllResults == True:
            words = self.normalizeCasePunct(phrase).split()
            
            foundWords = set()
            for nword in reversed(range(1, len(words))):
                for ngram in self.window(words, nword):
                    ngram = " ".join(ngram)
                                        
                    if self.alreadySeen(foundWords, ngram):
                        ngramWords = ngram.split()
                        ratio = float(len(ngramWords))/len(words)
                        inexactSuggestions = self.cascadeSearch(searcher, reader, ngram, ratio)
                                                
                        if len(inexactSuggestions) > 0:
                            suggestions.extend(inexactSuggestions)

                            for word in ngramWords:
                                foundWords.add(word)

        # THIS NEEDS UNIT TESTED BAD
        if len(suggestions) > 0:
            cuiListUnique = set([each3[1] for each3 in sorted(zip([each2[0] for each2 in suggestions], map(lambda x: x["cui"], [each[1] for each in suggestions])), key=itemgetter(0,1), reverse=True)])
            cuiListNotUnique = [each4[1] for each4 in sorted(zip([each2[0] for each2 in suggestions], map(lambda x: x["cui"], [each[1] for each in suggestions])), key=itemgetter(0,1), reverse=True)]
            cuiListNotUniqueWithScore = sorted(zip([each2[0] for each2 in suggestions], map(lambda x: x["cui"], [each[1] for each in suggestions])), key=itemgetter(0,1), reverse=True)
            deDuped = [cuiListNotUniqueWithScore[cuiListNotUnique.index(uniqueCui)] for uniqueCui in cuiListUnique]

            alreadySeen = []
            deDupedSuggestions = []
            for elem in deDuped:
                for elem2 in suggestions:
                    if elem[0] == elem2[0] and elem[1] == elem2[1]["cui"] and elem2[1]["cui"] not in alreadySeen:
                        alreadySeen.append(elem2[1]["cui"])
                        deDupedSuggestions.append(elem2)
            
            suggestions = deDupedSuggestions
            
        reader.close()   
        return suggestions
    
    def cascadeSearch(self, searcher, reader, phrase, ratio):
        results = []
        
        # 1) Exact match
        query1 = TermQuery( Term("str", phrase))
        hits1 = searcher.search(query1, self._maxHits).scoreDocs
        
        if hits1 > 0:
            for hit in hits1:
                results.append( (100*ratio, self.getDocument(reader, hit) ) )
                
        # 2) Normalized match
        normPhrase = self.normalizeCasePunct(phrase)
        if results == [] or self._includeAllResults == True:
            query2 = TermQuery( Term("str_norm", normPhrase))
            hits2 = searcher.search(query2, self._maxHits).scoreDocs
            
            if hits2 > 0:
                for hit in hits2:
                    results.append( (90*ratio, self.getDocument(reader, hit) ) )
        
        # 3) Alpha sorted and normalized
        sortedPhrase = self.sortWords(normPhrase)
        if results == [] or self._includeAllResults == True:
            query3 = TermQuery( Term("str_sorted", sortedPhrase))
            hits3 = searcher.search(query2, 1).scoreDocs
            
            # May need length instead of just hits3        
            if hits3 > 0:
                for hit in hits3:
                    results.append( (80*ratio, self.getDocument(reader, hit) ) )
                    
        # 4) Normalized and Stemmed
        stemmedPhrase = self.stemWords(normPhrase)
        if results == [] or self._includeAllResults == True:
            
            query4 = TermQuery( Term("str_stemmed", stemmedPhrase))
            hits4 = searcher.search(query4, 1).scoreDocs
            
            # May need length instead of just hits3        
            if hits4 > 0:
                for hit in hits4:
                    results.append( (70*ratio, self.getDocument(reader, hit) ) )
                    
        # 5) Normalized, Alpha sorted, and Stemmed
        stemmedSortedPhrase = self.stemWords(sortedPhrase)
        if results == [] or self._includeAllResults == True:
            
            query5 = TermQuery( Term("str_stemmedSorted", stemmedSortedPhrase))
            hits5 = searcher.search(query5, 1).scoreDocs
            
            # May need length instead of just hits3        
            if hits5 > 0:
                for hit in hits5:
                    results.append( (60*ratio, self.getDocument(reader, hit) ) )
                    
        return results
    
    def buildIndex(self, inputFile):
        analyzer = self.getAnalyzer()
        iwconf = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        
        iwconf.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter( SimpleFSDirectory( File(self.luceneDir) ), iwconf)
        
        # read through input file and write out to lucene
        counter = 0
        linesReadCounter = 0
        
        with open(inputFile, 'r') as lines:
            linesRead = 0
            
            for line in lines:
                try:
                    linesRead+=1
                    
                    if linesRead % 1000 == 0:
                        print "%d lines read" % linesRead
                        
                    cui, concept = line.replace("\",\"", "\t").replace("\"", "").split("\t")
                    concept = concept.strip()
                    cui = cui.strip()
                    
                    strNorm = self.normalizeCasePunct(concept)
                    strSorted = self.sortWords(strNorm)
                    strStemmed = self.stemWords(strNorm)
                    strStemmedSorted = self.stemWords(strSorted)
          
                    fdoc = Document()
                    
                    counter +=1
                    fid = counter
                    
                    fdoc.add( Field("id", unicode(fid), Field.Store.YES, Field.Index.NOT_ANALYZED))
                    fdoc.add( Field("cui", cui, Field.Store.YES, Field.Index.NOT_ANALYZED))
                    fdoc.add( Field("str", concept, Field.Store.YES, Field.Index.NOT_ANALYZED))
                    fdoc.add( Field("str_norm", strNorm, Field.Store.YES, Field.Index.NOT_ANALYZED))
                    fdoc.add( Field("str_sorted", strSorted, Field.Store.YES, Field.Index.NOT_ANALYZED))
                    fdoc.add( Field("str_stemmed", strStemmed, Field.Store.YES, Field.Index.NOT_ANALYZED))
                    fdoc.add( Field("str_stemmedSorted", strStemmedSorted, Field.Store.YES, Field.Index.NOT_ANALYZED))
                    writer.addDocument(fdoc)
                    if fid % 1000 == 0:
                        writer.commit()
                except:
                    "Skipping line: %s" % line
                    
        writer.commit()
        writer.close()

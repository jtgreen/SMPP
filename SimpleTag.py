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

class SimpleTag:
	"""
	This is simply a base class. A kind of an interface in the Java sense. 
	"""
	
	def _callAndNormalizeTagger(self, s):
		"""
		Return:		Normalized output, see calling function return.
		Signature:	s - a string to be tagged.
		
		Simply call the base tagger (e.g., the MedicalQueryParser or Ctakes for instance) and normalize its output.
		"""
		
		pass
	
	def tagSentence(self, sentence):
		"""
		Return:		a list of tagged parts of a single sentence. The form is a list of concepts in a tuple of three elements.
					The first index is the UMLS concept ID.
					The second index is subject of analysis in UIMA terms. E.g., it is the phrase that was tagged.
					The third index is the negation if applicable to the logic of the extending class, else default to False.
					
		Signature:	sentence - a single sentence as input.
		"""
		
		cuis = [ ('C000000', 'sofa', 'False'), ]
		
		return cuis
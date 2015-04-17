import SimpleTag
from MedicalQueryParser.MedicalQueryParser import MedicalQueryParser
from Negex import negex

class SimpleTag_MedicalQueryParser(SimpleTag.SimpleTag):
	"""		
	Init: medicalQueryParserIndexLocation, negexRuleFileLocation, includeAllResults=False, maxHits=10
	"""
	
	def __init__(self, medicalQueryParserIndexLocation, negexRuleFileLocation, includeAllResults=False, maxHits=10):
		# Instantiate an instance of medicalQueryParser
		try:
			self.mqpTagger = MedicalQueryParser(medicalQueryParserIndexLocation, includeAllResults, maxHits)
		except IOError:
			# FEATURE ADD
			print "Unable to open MedicalQueryParser index."
		
		# Load Negex rule file
		try:
			rfile = open(negexRuleFileLocation)
			self.negexRules = negex.sortRules(rfile.readlines())
		except IOError:
			# FEATURE ADD
			print "Unable to load NegEx rule file."
			
	def _callAndNormalizeTagger(self, s):
		concepts = self.mqpTagger.annotateConcepts(s)
		return [ (concept[1]["cui"], concept[1]["str"], negex.negTagger(s, [ concept[1]["str"] ], self.negexRules, False).getNegationFlag() ) for concept in concepts ]
			
	def tagSentence(self, sentence):
		"""
		Return:		a list of tagged parts of a single sentence. The form is a list of concepts in a tuple of three elements.
					The first index is the UMLS concept ID.
					The second index is subject of analysis in UIMA terms. E.g., it is the phrase that was tagged.
					The third index is the negation if applicable to the logic of the extending class, else default to False.
					
		Signature: 	a sentence to tag.
		"""
		return self._callAndNormalizeTagger(sentence)

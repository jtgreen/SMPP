import lucene

from MedicalQueryParser import MedicalQueryParser

lucene.initVM(vmargs=['-Djava.awt.headless=true'])

# Set to True if you want the cascade not to short circuit at earlier steps. This, in effect, makes the algo act like a BOWs;
# Though you do still get the result scores by which to differentiate.
mqp = MedicalQueryParser("./Data/UMLSIndex", False, 100)

while True:
    print
    print "Hit enter with no input to quit."
    query = raw_input("Query:")
    if query == '':
        break
    else:
        for concept in mqp.annotateConcepts(query):
            print concept

import lucene

from MedicalQueryParser import MedicalQueryParser

lucene.initVM(vmargs=['-Djava.awt.headless=true'])

mqp = MedicalQueryParser("./Data/UMLSIndex", True, 100)

while True:
    print
    print "Hit enter with no input to quit."
    query = raw_input("Query:")
    if query == '':
        break
    else:
        for concept in mqp.annotateConcepts(query):
            print concept

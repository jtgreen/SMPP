import lucene
lucene.initVM(vmargs=['-Djava.awt.headless=true'])

from SimpleTag_MedicalQueryParser import SimpleTag_MedicalQueryParser
smqp = SimpleTag_MedicalQueryParser("./Data/umlsindex", "./Negex/negex_triggers.txt")

while True:
    print
    print "Hit enter with no input to quit."
    query = raw_input("Query:")
    if query == '':
        break
    else:
        for concept in smqp.tagSentence(query):
            print concept
    

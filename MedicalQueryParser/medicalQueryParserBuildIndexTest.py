import lucene

from MedicalQueryParser import MedicalQueryParser

lucene.initVM(vmargs=['-Djava.awt.headless=true'])

mqp = MedicalQueryParser("./Data/UMLSIndex")
mqp.buildIndex("./Data/cuistr.csv")

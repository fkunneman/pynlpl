#!/usr/bin/env python
#-*- coding:utf-8 -*-

from pynlpl.formats.timbl import TimblOutput
from pynlpl.statistics import Distribution
import codecs

class WSDSystemOutput(object):
    def __init__(self, filename = None):
        self.data = {}
        if filename:
            self.load(filename)

    def append(self, word_id, senses):
       assert (not word_id in self.data)
       if isinstance(senses, Distribution):
            self.data[word_id] = senses
            return
       else:
           assert isinstance(senses, list) and len(senses) >= 1

       if len(senses[0]) == 1:
            #not a (sense_id, confidence) tuple! compute equal confidence for all elements automatically:
            confidence = 1 / float(len(senses))
            self.data[word_id]  = [ (x,confidence) for x in senses ]
       else: 
          fulldistr = True
          for sense, confidence in senses:
            if confidence == None: 
                fulldistr = False
                break

          if fulldistr:
               self.data[word_id] = Distribution(senses)
          else:
               self.data[word_id] = senses

    def __iter__(self):
        for word_id, senses in  self.data.items():
            yield word_id, senses

    def load(self, filename):
        f = codecs.open(filename,'r','utf-8')
        for line in f:
            fields = line.split(" ")
            word_id = fields[0]
            if len(fields[1:]) == 1:
                #only one sense, no confidence expressed:
                self.append(word_id, [(fields[1],None)])
            else:
                senses = []
                for i in range(1,999,2):
                    senses.append( (fields[i], fields[i+1]) )
                self.append(word_id, senses)
        f.close()

    def save(self, filename):
        f = codecs.open(filename,'w','utf-8')
        for word_id, senses in self:
            f.write(word_id)
            for sense, confidence in senses:
                f.write(" " + sense + " " + str(confidence))
            f.write("\n")
        f.close()

    def loadfromtimbl(self, filename):
        timbloutput = TimblOutput(codecs.open(filename,'r','utf-8'))
        sysout = WSDSystemOutput()
        for features, referenceclass, predictedclass, distribution in timbloutput:
            word_id = features[0] #note: this is an assumption that must be adhered to!
            self.append(word_id, distribution)
            


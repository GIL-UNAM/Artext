# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 12:31:23 2021

@author: Abigail Ríos Guzmán
"""

from sinDict import *
import re

class char():
    def __init__(self):
        pass
    
class char_line():
    def __init__(self, word):
        self.word = word
        self.char_line = [(char, self.char_type(char)) for char in word]
        self.type_line = ''.join(chartype for char, chartype in self.char_line)
        
    def char_type(self, char):
        if char in set(['a', 'á', 'e', 'é','o', 'ó', 'í', 'ú']):
            return 'V' #strong vowel
        if char in set(['i', 'u']):
            return 'v' #week vowel
        if char=='x':
            return 'x'
        if char=='s':
            return 's'
        else:
            return 'c'
            
    def find(self, finder):
        return self.type_line.find(finder)
        
    def split(self, pos, where):
        return char_line(self.word[0:pos+where]), char_line(self.word[pos+where:])
    
    def split_by(self, finder, where):
        split_point = self.find(finder)
        if split_point!=-1:
            chl1, chl2 = self.split(split_point, where)
            return chl1, chl2
        return self, False
     
    def __str__(self):
        return '<'+self.word+':'+self.type_line+'>'
    
    def __repr__(self):
        return '<'+repr(self.word)+':'+self.type_line+'>'

class silabizer():
    def __init__(self):
        self.grammar = []
        
    def split(self, chars):
        rules  = [('VV',1), ('cccc',2), ('xcc',1), ('ccx',2), ('csc',2), ('xc',1), ('cc',1), ('vcc',2), ('Vcc',2), ('sc',1), ('cs',1),('Vc',1), ('vc',1), ('Vs',1), ('vs',1), ('vxv',1), ('VxV',1), ('vxV',1), ('Vxv',1)]
        for split_rule, where in rules:
            first, second = chars.split_by(split_rule,where)
            if second:
                if first.type_line in set(['c','s','x','cs']) or second.type_line in set(['c','s','x','cs']):
                    #print 'skip1', first.word, second.word, split_rule, chars.type_line
                    continue
                if first.type_line[-1]=='c' and second.word[0] in set(['l','r']):
                    continue
                if first.word[-1]=='l' and second.word[-1]=='l':
                    continue
                if first.word[-1]=='r' and second.word[-1]=='r':
                    continue
                if first.word[-1]=='c' and second.word[-1]=='h':
                    continue
                return self.split(first)+self.split(second)
        return [chars]
        
    def __call__(self, word):
        return self.split(char_line(word))

class TextSimplifier:
    def __init__(self, silabizer, txtLines):
        self.silabizer = silabizer
        self.txtLines = txtLines
        self.wordsChanged = {}
        
    def lowerList(self, list):
        newList = []
        for el in list:
            newList.append(el.lower())

        return newList
    
    def getNumberOfSyllables(self, word):    
        syllables = self.silabizer(word) # Syllables of word
        return len(syllables)
    
    def getShortestSynonymousWordInList(self, list, initialWord):
        word = initialWord
        for w in list:
            numOfSylWord = self.getNumberOfSyllables(word)
            if self.getNumberOfSyllables(w) < numOfSylWord:
                word = w
            
        return word
    
    def addToList(self, synList, dup, loweredList, lcWord):
        for el in loweredList:
            if el not in dup and el != lcWord:
                dup[el] = True
                synList.append(el)
                
        return synList, dup
    
    def changeWord(self, word):
        lcWord = word.lower() # Word in lower case
        
        if lcWord in self.wordsChanged:
            return self.wordsChanged[lcWord][0]
        else:
            newWord = word # New word
            synDictLength = len(synonyms)
            dup = {}
            synonymsList = []
        
            for i in range(synDictLength):
                synLoweredList = self.lowerList(synonyms[i]) # Synonims in lower case
                if lcWord in synLoweredList:
                    synonymsList, dup = self.addToList(synonymsList, dup, synLoweredList, lcWord)
                    #newWord = self.getShortestSynonymousWordInList(synonyms[i], word)
                    tempWord = self.getShortestSynonymousWordInList(synonyms[i], word)
                    newWord = tempWord if self.getNumberOfSyllables(tempWord) < self.getNumberOfSyllables(newWord) else newWord
            
            synonymsList.sort(key=self.getNumberOfSyllables)
            self.wordsChanged[lcWord] = synonymsList
            return newWord
    
    def replaceText(self):
        numOfLines = len(self.txtLines) # Number of lines
        replacementText = "" # Returned text
        
        for i in range(0, numOfLines):
            line = self.txtLines[i]
            
            # Remove char '\n' in the lines
            # Except in the last line
            if(i != numOfLines - 1):
                line = line[:-1]
                
            # Parse the words fot the i-th line
            words = line.split(" ")
            
            # Empty line
            line = ""
            
            # Check words in i-th line
            for word in words:
                numOfSyllables = self.getNumberOfSyllables(word)
                
                newWord = word # Save the initial word
                
                # If word has more then 3 syllables, changes the word
                if numOfSyllables > 3:
                    newWord = self.changeWord(word)
                
                # Add la new word
                line += newWord + " "
            
            line = line[:-1] # Remove the last space
            
            # Insert newline if it's not the last line
            if i != numOfLines - 1:
                line += "\n"
                
            replacementText += line
            
        return replacementText
    
    def getOptions(self):
        optionsStr = ""
        
        for word in self.wordsChanged:
            optionsStr += word + ":\n" + \
                str(self.wordsChanged[word])[1:-1] + '\n\n'
                
        return optionsStr
    
class SynonymsFinder:
    
    def __init__(self, silabizer, listOfSynonyms):
        self.silabizer = silabizer # Silabizer instance
        self.listOfSynonyms = listOfSynonyms # List of lists of synonyms
        self.words = {} # Big words dictionary
        
    def writeWordsToExcel(self, wb, filename):
    
        sheet = wb.add_sheet("Sinónimos", cell_overwrite_ok=True) # Add a sheet to write on
        x, y = 0, 0
        
        for w in self.words:
            sheet.write(y, x, w)
            sheet.write(y, x+1, self.words[w])
            y += 1
            
        wb.save("test.xls")
        
        return None
    
    def getNumberOfSyllables(self, word):    
        syllables = self.silabizer(word) # Syllables of word
        return len(syllables)

    def checkInListForSynonyms(self, l, word):
        first3Chars = word.lower()[:3]
        
        for w in l:
            if word != w:
                loweredWord = w.lower() # Current word in lower case
                wordToCheckAgainst = ""
                
                if w in self.words:
                    wordToCheckAgainst = self.words[w]
                else:
                    wordToCheckAgainst = word
    
                testWord = re.search("^" + first3Chars, loweredWord)
                wSyllables = self.getNumberOfSyllables(w)
                wordToCheckAgainstSyllables = self.getNumberOfSyllables(wordToCheckAgainst)
                
                if testWord and wSyllables < wordToCheckAgainstSyllables:
                    self.words[word] = w
                
    
    def processLargeWords(self):
        for words in self.listOfSynonyms:
            for word in words:
                if self.getNumberOfSyllables(word) >= 5:
                    self.checkInListForSynonyms(words, word)
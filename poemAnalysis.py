# -*- coding: utf-8 -*-

# Python script for analyzing phonemic data from IPA-encoded poems

# Copyright (C) 2015 Kris P. Shaffer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import codecs
import csv
import numpy
import fnmatch
from os import listdir

class threedim(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

def threedimdistance(i, j):
    deltaxsquared = (i.x - j.x) ** 2
    deltaysquared = (i.y - j.y) ** 2
    deltazsquared = (i.z - j.z) ** 2
    return (deltaxsquared + deltaysquared + deltazsquared) ** 0.5

def threedimmean(threedimlist):
    xvalues = []
    yvalues = []
    zvalues = []
    for point in threedimlist:
        xvalues.append(point.x)
        yvalues.append(point.y)
        zvalues.append(point.z)
    xmean = sum(xvalues)/float(len(xvalues))
    ymean = sum(yvalues)/float(len(yvalues))
    zmean = sum(zvalues)/float(len(zvalues))
    return threedim(xmean, ymean, zmean)

def threedimSD(threedimlist):
    squareddistances = []
    listmean = threedimmean(threedimlist)
    for point in threedimlist:
        squareddistances.append(threedimdistance(point, listmean) ** 2)
    return (sum(squareddistances)/float(len(squareddistances)) ** 0.5)

class IPAText(object):

    def __init__(self, content):
        self.content = content

    def unicodeSet(self):
        unicodeSetRaw = []
        for line in self.content:
            for character in line:
                unicodeSetRaw.append(character)
        return set(unicodeSetRaw)

    def unicodeDictionary(self):
        unicodeCount = {}
        for phoneme in self.unicodeSet():
            unicodeCount[phoneme] = 0
        for line in self.content:
            for member in line:
                unicodeCount[member] += 1
        return unicodeCount

    def unicodeCount(self,character):
        unicodeCount = {}
        for phoneme in self.unicodeSet():
            unicodeCount[phoneme] = 0
        for line in self.content:
            for member in line:
                unicodeCount[member] += 1
        return unicodeCount[character]

    def parseGlyphByLine(self):
        i = 1
        outputData = []
        headerRow = []
        headerRow.append('Phoneme')
        for phoneme in self.unicodeSet():
            headerRow.append(phoneme.encode('utf-8'))
        outputData.append(headerRow)
        while i <= len(self.content):
            label = 'Line ' + str(i)
            outputLine = []
            outputLine.append(label)
            rawTally = {}
            categoryTally = {}
            for phoneme in self.unicodeSet():
                rawTally[phoneme] = 0
            phonemeTotal = 0

            j = 1 # character iterator
            for phoneme in self.content[i-1]:
                phonemeTotal += 1
                rawTally[phoneme] += 1
                j += 1

            for phoneme in self.unicodeSet():
                outputLine.append(rawTally[phoneme])

            i += 1
            outputData.append(outputLine)
        return outputData


    def parseCategoryProb(self, ignore, categoryDictionary, ignoreDiphthongs=True, moduleType = 'Line'):
        i = 1
        outputDataCategoryProbability = []
        phonemeCategoryList = list(set(categoryDictionary.values()))
        outputDataCategoryProbability.append(phonemeCategoryList)

        while i <= len(self.content):
            if self.content[i-1] != '':
                label = moduleType + ' ' + str(i)
                outputLineCategoryProbability = []
                # outputLineCategoryProbability.append(label)
                rawTally = {}
                categoryTally = {}
                for phoneme in self.unicodeSet():
                    rawTally[phoneme] = 0
                for category in phonemeCategoryList:
                    categoryTally[category] = 0
                phonemeTotal = 0
                categoryMemberTotal = 0

                j = 1 # character iterator
                for phoneme in self.content[i-1]:
                    if phoneme not in ignore:
                        phonemeTotal += 1
                    rawTally[phoneme] += 1
                    if phoneme in phonemeCategory.keys():
                        if ignoreDiphthongs == False or self.content[i-1][j-2] != ':':
                            categoryTally[phonemeCategory[phoneme]] += 1
                            if phonemeCategory[phoneme] in phonemeCategoryList:
                                categoryMemberTotal += 1
                    j += 1
                for category in phonemeCategoryList:
                    outputLineCategoryProbability.append(float(categoryTally[category])/float(categoryMemberTotal))

                outputDataCategoryProbability.append(outputLineCategoryProbability)
            i += 1

        return outputDataCategoryProbability


def writeToCSV(dataToWrite, outputFileName):
    with open(outputFileName, 'w') as csvfile:
        w = csv.writer(csvfile, delimiter=',')
        for row in dataToWrite:
            w.writerow(row)
    print outputFileName, 'successfully created.'


def getText(directory, filename):
    return [line.rstrip('\n') for line in codecs.open((directory + filename), encoding='utf-8')]

def stanzify(content):
    stanzas = ['']
    i = 0 # stanza counter
    j = 1 # line counter
    for line in content:
        if line != '':
            stanzas[i] += line
            stanzas[i] += ' '
            j += 1
        else:
            i += 1
        if j < len(content):
            stanzas.append('')
    return stanzas

def wholeSong(content):
    song = ['']
    for line in content:
        if line != '':
            song[0] += line
            song[0] += ' '
    return song

def stressedVowelsOnly(content, vowelList):
    stressedVowels = []
    for line in content:
        vowelLine = ''
        stressFlag = False
        for letter in line:
            #print letter, stressFlag
            if letter == "'":
                stressFlag = True
            if letter in vowelList and stressFlag == True:
                vowelLine += letter
                stressFlag = False
        if vowelLine:
            stressedVowels.append(vowelLine)
    return stressedVowels

def threeDimAnalysis(coordinatesList):
    linesAsThreeDim = []
    i = 0
    for lineOfText in coordinatesList:
        if i > 0:
            linesAsThreeDim.append(threedim(lineOfText[0], lineOfText[1], lineOfText[2]))
        i += 1
    songMean = threedimmean(linesAsThreeDim)
    songSD = threedimSD(linesAsThreeDim)

    outputAnalysis = []

    i = 0
    for lineOfText in coordinatesList:
        lineAnalysis = []
        if i == 0:
            lineAnalysis.append('lineNumber')
            for heading in lineOfText:
                lineAnalysis.append(heading)
            lineAnalysis.append('distFromPrev')
            lineAnalysis.append('ZNorm')
        else:
            lineAnalysis.append('line ' + str(i))
            for element in lineOfText:
                lineAnalysis.append(element)
            if i > 1:
                lineDistFromPrev = threedimdistance(linesAsThreeDim[i-1],linesAsThreeDim[i-2])
                lineAnalysis.append(lineDistFromPrev)
                lineAnalysis.append(lineDistFromPrev/songSD)
            else:
                lineAnalysis.append('NULL')
                lineAnalysis.append('NULL')
        i += 1
        outputAnalysis.append(lineAnalysis)
    return outputAnalysis

def combineCorpusAnalyses(listOfPoems):
    corpusOutput = []
    i = 0
    for poem in listOfPoems:
        poemLines = IPAText(getText(sourceDirectory, poem))
        poemAnalysis = threeDimAnalysis(poemLines.parseCategoryProb(ignore, phonemeCategory, moduleType = 'Line'))
        if i == 0:
            j = 0
            for line in poemAnalysis:
                lineOutput = []
                if j == 0:
                    lineOutput.append('poem')
                    j += 1
                else:
                    lineOutput.append(str(poem))
                for element in line:
                    lineOutput.append(element)
                corpusOutput.append(lineOutput)
        else:
            for line in poemAnalysis:
                if line[0] != 'lineNumber':
                    lineOutput = []
                    lineOutput.append(str(poem))
                    for element in line:
                        lineOutput.append(element)
                corpusOutput.append(lineOutput)
        i += 1
    return corpusOutput

# run

ignore=['.', ':', ' ']
phonemeCategory = {
    'a': 'open',
    'e': 'close',
    u'\u025b': 'open',
    u'\u0259': 'neutral',
    'i': 'close',
    'I': 'close',
    'o': 'close',
    u'\u0254': 'open',
    u'\u00f8': 'close',
    u'\u0153': 'open',
    'y': 'close',
    'u': 'close',
    u'\u028a': 'close',
    'Y': 'close',
}

phonemeCategoryFive = {
    'a': 'open',
    'e': 'closeMid',
    u'\u025b': 'openMid',
    u'\u0259': 'neutral',
    'i': 'close',
    'I': 'close',
    'o': 'closeMid',
    u'\u0254': 'openMid',
    u'\u00f8': 'closeMid',
    u'\u0153': 'openMid',
    'y': 'close',
    'u': 'close',
    u'\u028a': 'close',
   'Y': 'close',
}

vowelList = phonemeCategory.keys()

sourceDirectory = 'texts/'
outputDirectory = 'statOutput/'
poemCorpus = []
for file in listdir(sourceDirectory):
    if fnmatch.fnmatch(file, '*IPAMusic.txt'):
        poemCorpus.append(file)


writeToCSV(combineCorpusAnalyses(poemCorpus), (outputDirectory + 'corpus-3DAnalysisByLine.csv'))

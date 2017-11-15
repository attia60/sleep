import pyedflib
import numpy as np
import xml.etree.ElementTree as ET

def loadSignals(edfFilePath):
	edf = pyedflib.EdfReader(edfFilePath)
	signal_labels = edf.getSignalLabels()
	signals = {}
	for index, signal_label in enumerate(signal_labels):
		signals[signal_label] = edf.readSignal(index)
	return signals


def getArousalSignals(signalsDict):
	arousalSignals = {}
	arousalSignals['ECG'] = signalsDict['ECG R'] - signalsDict['ECG L']
	arousalSignals['ECG'] = arousalSignals['ECG'][0::2] #512Hz->256Hz to match others
	arousalSignals['EEG1'] = signalsDict['C3'] - signalsDict['A2']
	arousalSignals['EEG2'] = signalsDict['C4'] - signalsDict['A1']
	arousalSignals['M'] = signalsDict['L Chin'] - signalsDict['R Chin']
	return arousalSignals


def convertByFrequency(arousalPairs, frequency):
	for pair in arousalPairs:
		pair[0] = pair[0]*frequency
		pair[1] = pair[1]*frequency

def getArousalLabels(annotationFilename):
	
	tree = ET.parse(annotationFilename)
	root = tree.getroot()
	scored_events = root[2]

	arousalPairs = []
	for child in scored_events:
		event = child[0]
		event_type = child[0].text
		if event_type == 'Arousals|Arousals':
			start = float(child[2].text)
			end = start + float(child[3].text)
			arousalPairs.append([start,end])

	convertByFrequency(arousalPairs, 256)

	return arousalPairs

def writeCsvLine(outFile, header, numpyArr):	
	outFile.write(header + ",")
	outFile.write(','.join(map(str, numpyArr.tolist())))
	outFile.write('\n')

def getArousalArray(arousalLabels, numTimesteps):
	arousalArray = np.zeros(numTimesteps)
	for label in arousalLabels:
		start = int(label[0])
		end = int(label[1])
		for timeIndex in range(start, end):
			arousalArray[timeIndex] = 1
	return arousalArray


def writeXY(arousalSignals, arousalLabels, outFile):

	outFile = open(outFile, 'w')
	for signal in arousalSignals:
		writeCsvLine(outFile, signal, arousalSignals[signal])

	numTimesteps = len(arousalSignals[arousalSignals.keys()[0]]) 
	arousalArray = getArousalArray(arousalLabels, numTimesteps)
	writeCsvLine(outFile, 'ArousalLabel', arousalArray)

	outFile.close()

	
signals = loadSignals('sample.edf')
arousalSignals = getArousalSignals(signals)
labels = getArousalLabels('sample_annotation.xml')

#first 4 rows: signal type & val
#last row: arousal label per time index (second/256)
writeXY(arousalSignals, labels, 'outfile.csv')






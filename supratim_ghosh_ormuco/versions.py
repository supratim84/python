#!/usr/bin/env python
import re

# List of markers denoting pre-release versions
MARKER_LIST = ['-rc', ]

def _processVersionString(versionString):
	# Replaces the release candidate marker characters and strips tailing .0s
	cleanString = re.sub(r'|'.join(MARKER_LIST), '.', versionString)
	cleanString = re.sub(r'(\.0+)*$', '', cleanString)

	return list(map(int, cleanString.split('.')))


def versionCompare(versionStr1, versionStr2):
	"""	Compares the two version strings and returns the result in a
	readable string format

	@param str versionStr1: First version string
	@param str versionStr2: Second version string
	@return str: Readable message with comparison result
	"""
	messages = ['is equal to', 'is greater than', 'is less than']
	verList1 = _processVersionString(versionStr1)
	verList2 = _processVersionString(versionStr2)

	checkBit = (verList1 > verList2) - (verList1 < verList2)
	return '%s %s %s' % (versionStr1, messages[checkBit], versionStr2)


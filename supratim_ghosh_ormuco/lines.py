#!/usr/bin/env python

def doLinesOverlap(line1Pts, line2Pts):
	"""Checks if line1's span overlaps with line2's, assuming points
	are only on the X axis.

	@param tuple line1Pts: Tuple containing 2 points of first line on the x-axis
	@param tuple line2Pts: Tuple containing 2 points of second line on the x-axis
	@return bool: True if the span's overlap
	"""
	assert (len(line1Pts), len(line2Pts)) == (2, 2), 'Only tuples with 2 pts expected'
	(x1, x2), (x3, x4) = line1Pts, line2Pts
	
	return not(x3>x2 or x1>x4)
	

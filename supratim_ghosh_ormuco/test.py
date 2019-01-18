import unittest
import time
import lines
import versions
import lru_cache


class LinesTest(unittest.TestCase):
	"""Contains tests for Question A
	"""
	def testLinesOverlap(self):
		# Check if lines are overlapping
		self.assertTrue(lines.doLinesOverlap((1, 5), (5, 8)))
		self.assertTrue(lines.doLinesOverlap((1, 5), (4, 8)))

	def testLinesDoNotOverlap(self):
		# Check if lines are not overlapping
		self.assertFalse(lines.doLinesOverlap((1, 2), (3, 5)))
		self.assertFalse(lines.doLinesOverlap((5, 6), (3, 4)))
	

class VersionsTest(unittest.TestCase):
	"""Contains tests for Question B
	"""
	def setUp(self):
		self.isLT = 'is less than'
		self.isET = 'is equal to'
		self.isGT = 'is greater than'

	def _assert(self, v1, res, v2):
		self.assertTrue(
			versions.versionCompare(v1, v2), 
			'%s %s %s' % (v1, res, v2)
		) 

	def testVersionCompare(self):
		# Runs multiple checks
		self._assert('1.1', self.isET, '1.1') 	
		self._assert('1.1.1', self.isET, '1.1.1')
		self._assert('1.1.1.1', self.isET, '1.1.1.1')
		self._assert('1.1', self.isET, '1.1.0') 	
		self._assert('1.01', self.isET, '1.1')
		self._assert('1.1.1.000', self.isET, '1.1.1')
 	
		self._assert('1.100', self.isGT, '1.2') 
		self._assert('2.0', self.isGT, '1.999') 
		self._assert('2.1', self.isGT, '2.0') 
		self._assert('1.1-rc1', self.isGT, '1.1') 	
		self._assert('1.1.1.100', self.isGT, '1.1.1.099') 	
		self._assert('1.2.3-rc2', self.isGT, '1.2.3-rc1') 	
	
		self._assert('1.0', self.isLT, '1.2') 	
		self._assert('1.0', self.isLT, '2.0') 	
		self._assert('1.1.100', self.isLT, '1.1.100.1') 	
		self._assert('1.2.3-rc1', self.isLT, '1.2.3-rc2') 	
		self._assert('0.99', self.isLT, '2.0') 	


class LRUCacheTest(unittest.TestCase):
	@lru_cache.LRUCache(ttl=3)
	def dieIn3Seconds(var1, var2):
		return var1 + var2

	@lru_cache.LRUCache(ttl=10)
	def dieIn10Seconds(var1, var2):
		return var1 + var2 

	def testCacheClearOnTimeout(self):
		masterCache = lambda : list(map(lambda v: (v[0].__name__, v[1]), lru_cache.LRUCache()._masterCacheDict.items()))
		# Confirm that cache is empty in the begining
		self.assertListEqual(masterCache(), [('dieIn3Seconds', {}), ('dieIn10Seconds', {})])

		# Register first item in cache
		LRUCacheTest.dieIn3Seconds(1, 2)
		dieIn3Entry1 = dict(masterCache())['dieIn3Seconds']
		# Confirm that we set cache
		self.assertNotEqual(dieIn3Entry1, {})
		# Let it timeout
		time.sleep(4)
		lru_cache.LRUCache()._clear()
		self.assertListEqual(masterCache(), [('dieIn3Seconds', {((1, 2), ()): {}}), ('dieIn10Seconds', {})])

	
if __name__=='__main__':
	unittest.main()	

import time


class LRUCache:
	"""Caching class implementing a basic memoization with timeout
	"""
	_masterTTLDict = {}
	_masterCacheDict = {}
	
	def __init__(self, ttl=3):
 		# Default time to live is set to 3 seconds
		self.ttl = ttl
	
	def __call__(self, func):
		# Wrapper to perform basic time base dict lookup
		self._masterTTLDict[func]  = self.ttl
		self._thisCache = self._masterCacheDict[func] = {}
		
		def wrapper(*args, **kwargs):
			key = (args, tuple(sorted(kwargs.items(), key=lambda x: x[0])))
			try:
				value = self._thisCache[key]
				if (time.time() - value[1]) > self.ttl:
					raise KeyError
			except KeyError:
				# Cache the function identifier with the current time
				value = self._thisCache[key] = (func(*args, **kwargs), time.time())

			return value[0]	

		return wrapper

	def _clear(self):
		for func, funcCaches in self._masterCacheDict.items():
			for funcCacheKey, cacheVal in funcCaches.items():
				if (time.time() - cacheVal[1]) > self._masterTTLDict[func]:
					self._masterCacheDict[func][funcCacheKey] = {}
			

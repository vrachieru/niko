class Cache():
	def bootstrap_cache(self):
		if not hasattr(self, "cache"):
			if hasattr(self, "bot") and hasattr(self.bot, "cache"):
				self.cache = self.bot.cache
			else:
				self.cache = {}

	def save(self, key, value):
		self.bootstrap_cache()
		self.cache.update({ key:value })

	def load(self, key):
		self.bootstrap_cache()
		return self.cache[key]
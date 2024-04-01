import hashlib
import requests



# a = '''“We have over 100,000 children, which we’ve never had before, in serious condition, and many on ventilators” due to the coronavirus.'''
def fetch_from_url(url):
	return url

def sha256_hash(data):
	sha256 = hashlib.sha256()
	sha256.update(data.encode("utf-8"))
	hashed_data = sha256.hexdigest()
	return hashed_data

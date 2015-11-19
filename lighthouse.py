#!/usr/bin/python
"""
Lighthouse

Update Route53 domain 'A' level resources with your current external IP.

By: Noah Kipin
Date: 2015-11-18
"""
import logging
import argparse
import urllib2
import boto3

def init():
	logging.basicConfig(level=logging.DEBUG,
						format='%(asctime)s %(message)s')
	parser = argparse.ArgumentParser(description='UPSERT Route53 names')
	parser.add_argument('--loglevel')

def main():
	currentIP = getExternalIP()
	if (!currentIP):
		logging.error('Unable to retrieve external IP')



def getCurrentRecord():
	pass

def getExternalIP():
	logging.debug('Retrieving external IP')
	try:
		extIPResource = urllib2.urlopen('https://api.ipify.org')
	except URLError:
		logging.error(URLError)
		return False
	logging.debug("Status: %i", extIPResource.getcode())
	if (extIPResource.getcode() == 200):
		externalIP = extIPResource.read(20)
		logging.debug('External IP: %s', externalIP)
		return externalIP
	else:
		return False
		
def postIP(name, oldip, newip):
	ChangeBatch = {
		'Changes': [
			{
				'Action': 'UPSERT',
				'ResourceRecordSet': {
					'Name': name,
					'Type': 'A',
					'TTL': 2
				}
			}
		]
	}
	pass

if __name__ == '__main__':
	init()
	main()

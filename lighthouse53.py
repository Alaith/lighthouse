#!/usr/bin/python
"""
lighthouse53

UPSERT a Route53 dns resource record with your current external IPv4 address.

Noah Kipin <nkipin@gmail.com>
2015-11-18
"""
import logging
import argparse
import urllib2
import boto3

def init():
	parser = argparse.ArgumentParser(description='UPSERT a Route53 resource with your current external IPv4 address')
	parser.add_argument('--loglevel')
	parser.add_argument('--ttl')
	parser.add_argument('hostedZoneId')
	parser.add_argument('name')
	#parser.add_argument('--type') need an external IPv6 API to do AAAA
	logging.basicConfig(
		filename='/var/log/lighthouse53',
		level=logging.DEBUG,
		format='%(asctime)s %(message)s')
	return parser.parse()

def main():
	currentIP = getExternalIP()
	if (!currentIP):
		logging.error('Unable to retrieve external IP')
		return 100
	client = boto3.client('route53')
	currentReccord = getCurrentRecord(client, hostedZoneId, name)
	if (!currentReccord):
		logging.error('Unable to retrieve current record')
		return 200
	if(currentIP == currentReccord):
		logging.info('No change')
		return 0
	else:
		logging.info('')

def getCurrentRecord(client, hostedZoneId, name):
	response = client.list_resource_record_sets(
		HostedZoneId = hostedZoneId,
		StartRecordName = name,
		StartRecordType = 'A',
		MaxItems='1')
	return response['ResourceRecordSets'][0]['ResourceRecords'][0]['Value']

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
		
def postIP(client, hostedZoneId, name, newip):
	changeBatch = {
		'Changes': [
			{
				'Action': 'UPSERT',
				'ResourceRecordSet': {
					'Name': name,
					'Type': 'A',
					'TTL': ttl,
					'ResourceRecords': [
						{
							'Value': newip
						}
					]
				}
			}
		]
	}
	response = client.change_resource_record_sets(HostedZoneId = hostedZoneId, ChangeBatch = changeBatch)
	loggin.debug('Change submitted')
	if (response['Status'] == "PENDING"):
		waiter = client.get_waiter('resource_record_sets_changed')
		logging.debug('Change pending')
		waiter.wait(Id=response['Id'])
	logging.debug('Change insync')

if __name__ == '__main__':
	config = init()
	return main(config)

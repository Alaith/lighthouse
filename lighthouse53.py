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
	parser = argparse.ArgumentParser(
		description='UPSERT a Route53 resource with your current external IPv4 address')
	parser.add_argument('--loglevel', choices=['CRITICAL','ERROR','WARN','INFO','DEBUG'], type=str, help="The logging level you wish to see in the log file.", default='WARN')
	parser.add_argument('--ttl', help="The time to live (ttl) that you wish to have assigned for the record",type=int,default=7200)
	parser.add_argument('name', type=str, help="The domain record name to upsert")
	parser.add_argument('hostedZoneId', type=str, help="The hostedZoneId in which this route53 domain is hosted")
	#parser.add_argument('--type') need an external IPv6 API to do AAAA
	config = parser.parse_args()
	logLevels = {
		'CRITICAL': 50,
		'ERROR': 40,
		'WARN': 30,
		'INFO': 20,
		'DEBUG': 10
	}
	logging.basicConfig(
		filename='/var/log/lighthouse53',
		level=logLevels[config.loglevel],
		format='%(asctime)s %(message)s')
	return config

def main(config):
	logging.debug(config)
	currentIP = getExternalIP()
	if (currentIP == False):
		logging.error('Unable to retrieve external IP')
		return 
	client = boto3.client('route53')
	currentRecord = getCurrentRecord(client, config.hostedZoneId, config.name)
	if (currentRecord == None):
		logging.warn('Unable to retrieve current record')
	if(currentIP == currentRecord):
		logging.info('No change')
		return
	else:
		if (postIP(client, config.hostedZoneId, config.name, currentIP, config.ttl)):
			logging.info('Upsert with %s', currentIP)
			return 0
		else:
			logging.warn('Upsert failed')
			return 

def getCurrentRecord(client, hostedZoneId, name):
	logging.debug('Retrieving current record')
	try:
		response = client.list_resource_record_sets(
			HostedZoneId = hostedZoneId,
			StartRecordName = name,
			StartRecordType = 'A',
			MaxItems='1')
	except:
		logging.error('Error retrieving current record', exc_info = True)
		return None
	try:
		record = response.get('ResourceRecordSets')[0].get('ResourceRecords')[0].get('Value')
	except:
		logging.error('Error parsing response', exc_info = True)
		return None
	else:
		return record
		

def getExternalIP():
	logging.debug('Retrieving external IP')
	try:
		extIPResource = urllib2.urlopen('https://api.ipify.org')
	except:
		logging.error("Error retrieving external IP", exc_info = True)
		return False
	logging.debug("Status: %i", extIPResource.getcode())
	if (extIPResource.getcode() == 200):
		externalIP = extIPResource.read(20)
		logging.debug('External IP: %s', externalIP)
		return externalIP
	else:
		return False
		
def postIP(client, hostedZoneId, name, newip, ttl):
	logging.debug('Changing resource record')
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
	try:
		response = client.change_resource_record_sets(HostedZoneId = hostedZoneId, ChangeBatch = changeBatch)
	except:
		logging.error("Error submitting change request", exc_info = True)
		return False
	if (response.get('ChangeInfo').get('Status') == "PENDING"):
		logging.debug('Change pending')
		waiter = client.get_waiter('resource_record_sets_changed')
		try:
			waiter.wait(Id=response.get('ChangeInfo').get('Id'))
		except:
			logging.error("Error waiting for change", exc_info = True)
			return False
	logging.debug('Change insync')
	return True

if __name__ == '__main__':
	config = init()
	main(config)

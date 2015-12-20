#!/usr/bin/python
"""
lighthouse53

UPSERT a Route53 dns resource record with your current external IPv4 address.

Noah Kipin <nkipin@gmail.com>
2015-11-18

Licensed Under the GNU GPLv2
"""
import logging
import argparse
import urllib2
import boto3

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def main(hostedZoneId, name, ttl):
	logger.debug("zoneId: {}, name: {}, ttl: {}".format(hostedZoneId,name,ttl))
	currentIP = getExternalIP()
	if (currentIP == None):
		logger.error('Unable to retrieve external IP')
		return 1
	route53client = boto3.client('route53')
	currentRecord = getCurrentRecord(route53client, hostedZoneId, name)
	if(currentIP == currentRecord):
		logger.info('No change')
		return 0
	else:
		if (postIP(route53client, hostedZoneId, name, currentIP, ttl)):
			logger.info('Upsert with %s complete', currentIP)
			return 0
		else:
			return 1

def getCurrentRecord(route53client, hostedZoneId, name):
	logger.debug('Retrieving current resource record')
	try:
		response = route53client.list_resource_record_sets(
			HostedZoneId = hostedZoneId,
			StartRecordName = name,
			StartRecordType = 'A',
			MaxItems='1')
	except:
		logger.error('Error retrieving current resource record', exc_info = True)
		return None
	try:
		record = response.get('ResourceRecordSets')[0].get('ResourceRecords')[0].get('Value')
	except IndexError:
		logger.info('Resource record not present')
		return None
	except:
		logger.error('Error parsing resource record response', exc_info = True)
		return None
	else:
		return record
		

def getExternalIP():
	logger.debug('Retrieving external IP')
	try:
		extIPResource = urllib2.urlopen('https://api.ipify.org')
	except:
		logger.error("Error retrieving external IP", exc_info = True)
		return None
	logger.debug("Status: %i", extIPResource.getcode())
	if (extIPResource.getcode() == 200):
		externalIP = extIPResource.read(20)
		logger.debug('External IP: %s', externalIP)
		return externalIP
	else:
		return None
		
def postIP(route53client, hostedZoneId, name, newip, ttl):
	logger.debug('Changing resource record')
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
		response = route53client.change_resource_record_sets(HostedZoneId = hostedZoneId, ChangeBatch = changeBatch)
	except:
		logger.error("Error submitting resource record change request", exc_info = True)
		return False
	if (response.get('ChangeInfo').get('Status') == "PENDING"):
		logger.debug('Change pending')
		waiter = route53client.get_waiter('resource_record_sets_changed')
		try:
			waiter.wait(Id=response.get('ChangeInfo').get('Id'))
		except:
			logger.error("Error waiting for change request confimation", exc_info = True)
			return False
	#if the change is not pending, then it is INSYNC (or there was an error) -- boto3 docs
	logger.debug('Change confirmed')
	return True

if __name__ == '__main__':
	from logging.handlers import WatchedFileHandler
	parser = argparse.ArgumentParser(
		description='UPSERT a Route53 resource with your current external IPv4 address')
	parser.add_argument('--loglevel', choices=['CRITICAL','ERROR','WARN','INFO','DEBUG'], type=str, help="The logging level you wish to see in the log file. Default: 'WARN'", default='WARN')
	parser.add_argument('--ttl', help="The time to live (ttl) that you wish to have assigned for the record. Default: 7200",type=int,default=7200)
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
	logfh = WatchedFileHandler('/var/log/lighthouse53')
	logfh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))

	logger.setLevel(logLevels[config.loglevel])
	logger.addHandler(logfh)
	logging.getLogger('boto3').setLevel(logging.WARN)
	logging.getLogger('boto3').addHandler(logfh)

	main(config.hostedZoneId,config.name,config.ttl)
	logging.shutdown()
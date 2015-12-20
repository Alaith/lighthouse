<a title="By Letterofmarque (Own work) [CC BY-SA 3.0 (http://creativecommons.org/licenses/by-sa/3.0) or GFDL (http://www.gnu.org/copyleft/fdl.html)], via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File%3ASambroandcannons.jpg"><img width="256" alt="Sambroandcannons" src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Sambroandcannons.jpg/256px-Sambroandcannons.jpg"/></a>
#lighthouse53

Lighthouse53 is a simple dynamic DNS utility script. It upserts domain records in Amazon Web Services' Route53 with your network's public IP address.

##Requrements
* [boto3](https://github.com/boto/boto3) 

##Usage
```
usage: lighthouse53.py [-h] [--loglevel {CRITICAL,ERROR,WARN,INFO,DEBUG}]
                       [--ttl TTL]
                       name hostedZoneId

UPSERT a Route53 resource with your current external IPv4 address

positional arguments:
  name                  The domain record name to upsert
  hostedZoneId          The hostedZoneId in which this route53 domain is
                        hosted

optional arguments:
  -h, --help            show this help message and exit
  --loglevel {CRITICAL,ERROR,WARN,INFO,DEBUG}
                        The logging level you wish to see in the log file.
                        Default: 'WARN'
  --ttl TTL             The time to live (ttl) that you wish to have assigned
                        for the record. Default: 7200
```
You will need to have your AWS credentials in a location that boto3 can find them by following their [configuration guide](https://boto3.readthedocs.org/en/latest/guide/quickstart.html#configuration).

Logging is done in /var/log/lighthouse53

###Example:
From the shell:
```
./lighthouse53.py --ttl 1200 your.domain.com Z372ZZZOS353PM
```

I run the script with cron every 20 minutes to update a domain with my household IP:
```
*/20 * * * * /opt/lighthouse53/lighthouse53 --loglevel INFO --ttl 1200 redacted.xyz XXXXXXXXXXXXXX
```

##License
This software is licensed under the GNU GPLv2

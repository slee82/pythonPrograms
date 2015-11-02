# Sam Lee
# Programmatically create an AWS EC2 instance

import boto.ec2
import time
import sys


myImage = 'ami-5189a661'  # ubuntu-trusty-14.04-amd64-server-20150325 (ami-5189a661)


def main(argv):
	if len(sys.argv) != 1:
		print 'usage: python createAWSinstance.py'
		sys.exit()
	# create connection to AWS
	conn = boto.ec2.connect_to_region('us-west-2',
		aws_access_key_id='AKIAI6GDBSTDPTJE6SQA',
		aws_secret_access_key= '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')

	# # create security group
	secName = 'Sam-%d' % int(time.time())
	myHttpSsh = conn.create_security_group(secName, 'Sam Group')
	myHttpSsh.authorize('tcp', 80, 80, '0.0.0.0/0')
	myHttpSsh.authorize('tcp', 22, 22, '0.0.0.0/0')

	# # create key pair
	keyName = 'autoGenKey-%d' % int(time.time())
	key_pair = conn.create_key_pair(keyName)
	key_pair.save('')


	# # create instance
	reservation = conn.run_instances(image_id=myImage, 
		min_count=1, max_count=1, 
		key_name=keyName, 
		instance_type='t2.micro',
		security_groups=[myHttpSsh.name])

	instance = ''
	# # wait for instance to start
	for r in conn.get_all_instances():
		if r.id == reservation.id:
			instance = r.instances[0]
			break
	
	print 'Please wait, Instance is starting..'

	print '..',
	while not instance.update() == 'running':
		print '.',
		time.sleep(1)
	print 'done'
	
	print 'Instance is ready!'
	print 'Public IP: %s' % instance.private_dns_name
	print 'Private IP: %s' % instance.public_dns_name
	print 'Please connect to it using the command below'
	print 'ssh -i %s.pem' % keyName ,
	print 'ubuntu@%s' % instance.public_dns_name



if __name__ == "__main__":
	main(sys.argv)
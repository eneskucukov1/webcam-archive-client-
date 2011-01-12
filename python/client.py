import settings

from wordpress_xmlrpc import AuthenticatedMethod, Client
from wordpress_xmlrpc.wordpress import WordPressBase

from optparse import OptionParser

import base64
import os
import pickle
import simplejson
import sys

class WebcamArchive(WordPressBase):
	definition = {
		'error': 'error',
	}
	
	def __str__(self):
		return self.status

class WebcamArchiveClient(AuthenticatedMethod):
	method_name = 'webcamarchive.upload'
	method_args = ('image','meta',)
	return_status = WebcamArchive

def main():
	usage = "Usage: %prog [options] arg"
	parser = OptionParser(usage)
	parser.add_option('-f', '--file', dest='image', help='Path to image file to upload')
	parser.add_option('-d', '--data', dest='meta', help='A pickled Python dictionary or JSON-encoded string of meta data to upload along with the image')
	parser.add_option('-v', '--verbose', action='store_true', dest='verbose')
	(options, args) = parser.parse_args()
	
	if not hasattr(options, 'image'):
		sys.stderr.write('Please provide an image name.\n')
		return 1
	
	if hasattr(options, 'meta'):
		try:
			# Check for Python dictionary
			if type(pickle.loads(options.meta)) == type(dict()):
				meta = pickle.loads(options.meta)
			# Check for JSON-encoded string
			else:
				meta = simplejson.loads(options.meta)
		except:
			sys.stderr.write('Please provide meta information in a valid Python dictionary or JSON format.\n')
			return 3
	else:
		meta = '{}'
	
	if not os.path.exists(options.image):
		sys.stderr.write('The file provided does not exist.\n')
		return 2
	
	wp = Client(settings.WP_XMLRPC_URL, settings.WP_USERNAME, settings.WP_PASSWORD)
	
	# Encode image to preserve data across HTTP request
	image_text = base64.encodestring(open(options.image,'rb').read())
	
	if options.verbose:
		sys.stdout.write('Calling WordPress XML-RPC API.\n')
	
	status = wp.call(WebcamArchiveClient(image_text, meta))
	
	if options.verbose:
		sys.stdout.write('Return status of WordPress XML-RPC call: ' + str(status) + '\n')
	
	return 0

if __name__ == '__main__':
	sys.exit(main())
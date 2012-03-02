import urllib2
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from cStringIO import StringIO
import settings


def cache_image(path):
    """ Gets the source image and saves it in S3.
    """
    # get the image from the source URL
    url = '%s%s' % (settings.source_url, path)
    try:
        image_file = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        if e.code == 404:
            return '404 NOT FOUND', False, ''
        raise
    image_data = StringIO(image_file.read())

    # connect to S3 and save the resized image to the target bucket
    conn = boto.connect_s3(settings.aws_access_key_id,
                           settings.aws_secret_access_key)
    bucket = conn.get_bucket(settings.target_bucket)
    k = Key(bucket)
    k.key = path
    k.set_contents_from_file(image_data)
    
    # TODO send proper headers
    headers = [('Content-type', image_file.info()['content-type'])]
    return '200 OK', headers, image_data.getvalue()

def app(environ, start_response):

    headers = False
    status, headers, data = cache_image(environ['PATH_INFO'])
    if not headers:
        # default headers in case of error
        headers = [('Content-type','text/plain')]

    start_response(status, headers)
    return [data]
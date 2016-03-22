#!/usr/bin/env python

from PIL import Image
import boto3
import json
import botocore
from urllib import unquote as urlunquote


class Mandel(object):
    def __init__(self, zoom, tilex, tiley, pixelsx=100, pixelsy=100,
                 defimagepixelsx=700, defimagepixelsy=400):
        print "zoom = %s, tilex = %s, tiley = %s" % (zoom, tilex, tiley)
        self.minx = -2.5
        self.maxx = 1.0
        self.miny = -1.0
        self.maxy = 1.0

        filename = '/tmp/tile.png'
        tile = Image.new("RGB", (pixelsx, pixelsy))

        pixels = []

        xstep = (self.maxx-self.minx)/(defimagepixelsx + (zoom * 140))
        ystep = (self.maxy-self.miny)/(defimagepixelsy + (zoom * 80))
        self.minx += xstep*100*tilex
        self.miny += ystep*100*tiley
        print "starting with x=%s, y=%s" % (self.minx , self.miny)
        for y in xrange(pixelsy):
            for x in xrange(pixelsx):
                xval = self.minx + (xstep * x)
                yval = self.miny + (ystep * y)
                pixels.append((0, 0, self.getBlue(xval, yval)))
        print "ending with x=%s, y=%s" % (xval, yval)
        tile.putdata(pixels)
        tile.save(filename, 'png')

    def getBlue(self, xval, yval):
        zorig = complex(xval, yval)
        z = complex(xval, yval)
        iteration = 0
        max_iteration = 50
        while abs(z) < 2 and iteration < max_iteration:
            z = z * z + zorig
            iteration += 1
        if iteration == max_iteration:
            color = 0
        else:
            if iteration <= 1:
                color = 255
            elif iteration == 2:
                color = 235
            elif iteration == 3:
                color = 215
            elif iteration <= 6:
                color = 180
            elif iteration <= 10:
                color = 150
            else:
                color = 100
        return int(color)


def lambda_handler(event, context):
    bucketname = 'dbarnetttestimageforlambda'
    tilex, tiley = urlunquote(event['coords']).strip("()").replace(' ', '').split(',')
    zoom = event['zoom']
    keyname = Key="%s:%s:%s" % (zoom, tilex, tiley)
    s3 = boto3.resource('s3')
    try:
        #s3.Bucket(bucketname).get_object(keyname)
        s3.Object(bucketname, keyname).load()
    except botocore.exceptions.ClientError as e:
        Mandel(int(zoom), int(tilex), int(tiley))
        s3.Bucket(bucketname).put_object(Key=keyname, Body=open('/tmp/tile.png', 'rb'))
    return json.loads('{"location": "https://s3-us-west-2.amazonaws.com/%s/%s"}' % (bucketname, keyname))

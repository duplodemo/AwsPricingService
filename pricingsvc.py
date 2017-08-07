from flask import Flask, jsonify
from flask import request
import subprocess
import threading
import time
from threading import Thread
import socket
import pdb
import logging
import json
import requests
import sys
import os
from logging import handlers, Formatter

app = Flask(__name__)
PriceData = {}
Disclaimer = 'This pricing list is for informational purposes only. We make no gurantee about the accuracy of the pricing. Use this at your own risk. THIS SERVICE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.' 

@app.route('/api/v1.0/testGet', methods=['GET'])
def testGet():
    return jsonify({'Price':'foo'})


@app.route('/api/v1.0/findOnDemandHourlyPrice', methods=['POST'])
def findOnDemandHourlyPrice():
    instanceType = request.json['instanceType']
    location = request.json['location']
    operatingSystem = request.json['operatingSystem']
    logger.debug(request.json)

    global PriceData
    hourlyTermCode = 'JRTCKXETXF'
    rateCode = '6YS6EN2CT7'
    print 'downloaded rates data'

    products = PriceData['products']
    price = ''
    for sku, properties in products.iteritems():
      if properties['productFamily'] == 'Compute Instance':
        if (properties['attributes']['instanceType'] == instanceType and
          properties['attributes']['location'] == location and
          properties['attributes']['operatingSystem'] == operatingSystem and
          properties['attributes']['tenancy'] == 'Shared' and
          properties['attributes']['preInstalledSw'] == 'NA' and
          properties['attributes']['licenseModel'] == 'No License required'):

            logger.debug('Found the desired sku')
            price = PriceData['terms']['OnDemand'][sku][sku + '.' + hourlyTermCode]['priceDimensions'][sku + '.' + hourlyTermCode + '.' + rateCode]['pricePerUnit']['USD']
            logger.debug(price)
   
    return jsonify({'Term':'Ondemand hourly', 'Price':price, 'disclaimer':Disclaimer})

def updatePriceCache():
    global PriceData
    url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json'
    resp = requests.get(url=url)
    PriceData = json.loads(resp.text)
    logger.debug('Downloaded and refreshed cache')    

def updatePriceCacheThread():
    while(True):
        try:
            updatePriceCache()
            #findPrice()    
        except Exception, e:
            err = "****************************** updatePriceCacheThread encountered an exception: %s" % e
            logger.error(err)

        logger.debug('================================= updatePriceCacheThread completed')
        time.sleep(6000)

def setLogger():
    logFile = "log/AwsPricingSvc.log"
    logger = logging.getLogger('AwsPricingSvc')

    fh = handlers.RotatingFileHandler(logFile, maxBytes=5000000, backupCount=5)
    logFormat = Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(logFormat)

    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    #
    # Detach stdout, stdin and stderr for daemonizing 
    #
    #    f = open('/dev/null', 'w')
    #sys.stdout = f
    #sys.stderr = f
    #sys.stdin.close()

    logger.debug('stdout/stderr redirected to /dev/null ...')

    return logger

def main():
    global logger
    logger = setLogger()
    global refresh_timer
    refresh_timer = os.getenv('REFRESH_TIMER', None)
    if refresh_timer is not None:
        logger.debug('Launching Pricing update Thread')
        thread = Thread(target = updatePriceCacheThread, args = [])
        thread.setDaemon(True)
        thread.start()
    else:
        logger.debug('One time cache update')
        updatePriceCache()
    # logger.debug('No thread version')
    # updatePriceCache()
    # findPrice()
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)


if __name__ == '__main__':
   main()



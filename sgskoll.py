import os
import urllib
import urllib2
import json

SEARCH_URL = 'http://marknad.sgsstudentbostader.se/API/Service/SearchServiceHandler.ashx'

SEARCH_PARAMS = {
    "Parm1": '{"CompanyNo":1,"SyndicateNo":1,"ObjectMainGroupNo":1,"Advertisements":[{"No":-1}],"RentLimit":{"Min":0,"Max":15000},"AreaLimit":{"Min":0,"Max":150},"Page":1,"Take":10,"SortOrder":"EndPeriodMP asc, CompanyNo asc,SeekAreaDescription asc,StreetName asc","ReturnParameters":["ObjectNo","FirstEstateImageUrl","Street","SeekAreaDescription","PlaceName","ObjectSubDescription","ObjectArea","RentPerMonth","MarketPlaceDescription","CountInterest","FirstInfoTextShort","FirstInfoText","EndPeriodMP","FreeFrom","SeekAreaUrl","Latitude","Longitude","BoardNo"]}',
    "CallbackMethod": 'PostObjectSearch',
    "CallbackParmCount": '1',
    "__WWEVENTCALLBACK": '' }

SEARCH_HEADERS = {
    "Accept": 'application/json,text/*',
    "X-Requested-With": 'XMLHttpRequest' }


def fetch():
    with open('Momentum-API-KEY.secret') as f:
        SEARCH_HEADERS["X-Momentum-API-KEY"] = f.read()
    request = urllib2.Request(SEARCH_URL,
                              urllib.urlencode(SEARCH_PARAMS),
                              SEARCH_HEADERS)
    return urllib2.urlopen(request)

def parse(fp):
    return json.load(fp)

if __name__ == '__main__':
    if not os.path.exists('sampledata'):
        print "Downloading data..."
        with open('sampledata', 'w') as f:
            f.write(fetch().read())

    data = parse(open('sampledata'))
    for obj in data["Result"]:
        print ("%(CountInterest)d %(Street)s") % obj



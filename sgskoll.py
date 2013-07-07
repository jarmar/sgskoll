#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import json
import ConfigParser
from itertools import ifilter

AREAS_URL = 'http://marknad.sgsstudentbostader.se/API/Service/SearchServiceHandler.ashx?objectMainGroupNo=1&visibleClient=true&visibleProfile=true&asTree=true&Method=GetSearchAreas'

SEARCH_URL = 'http://marknad.sgsstudentbostader.se/API/Service/SearchServiceHandler.ashx'

SEARCH_PARAMS = {
    "Parm1": '{"CompanyNo":1,"SyndicateNo":1,"ObjectMainGroupNo":1,"Advertisements":[{"No":-1}],"RentLimit":{"Min":0,"Max":15000},"AreaLimit":{"Min":0,"Max":150},"Page":1,"Take":10,"SortOrder":"EndPeriodMP asc, CompanyNo asc,SeekAreaDescription asc,StreetName asc","ReturnParameters":["ObjectNo","FirstEstateImageUrl","Street","SeekAreaDescription","PlaceName","ObjectSubDescription","ObjectArea","RentPerMonth","MarketPlaceDescription","CountInterest","FirstInfoTextShort","FirstInfoText","EndPeriodMP","FreeFrom","SeekAreaUrl","Latitude","Longitude","BoardNo"]}',
    "CallbackMethod": 'PostObjectSearch',
    "CallbackParmCount": '1',
    "__WWEVENTCALLBACK": '' }

SEARCH_HEADERS = {
    "Accept": 'application/json,text/*',
    "X-Requested-With": 'XMLHttpRequest' }


def fetch_search_data():
    u"""Hämta sökresultat. Returnerar file-like."""
    with open('Momentum-API-KEY.secret') as f:
        SEARCH_HEADERS["X-Momentum-API-KEY"] = f.read()
    request = urllib2.Request(SEARCH_URL,
                              urllib.urlencode(SEARCH_PARAMS),
                              SEARCH_HEADERS)
    return urllib2.urlopen(request)

def load_search_data(fp):
    u"""Generöst namngiven metod."""
    return json.load(fp)

def fetch_areas():
    u"""Hämta hem lista på områden. Returnerar file-like."""
    request = urllib2.Request(AREAS_URL, headers=SEARCH_HEADERS)
    return urllib2.urlopen(request)

def load_areas(fp):
    u"""Gör sans av den mottagna areadatan."""
    # dubbelt escapead json. enterprise!
    return get_areas_list(json.loads(json.load(fp)))

def get_areas_list(data, parentname=''):
    u"""Omvandla till mindre obtust format."""
    if data["Childs"] == []:
        return [{"Id": data["Id"],
                 "Description": data["Description"],
                 "Area": parentname}]
    res = []
    for child in data["Childs"]:
        res.extend(get_areas_list(child, data["Description"]))
    return res

def lookup_areas(userlist):
    u"""Hämta lista på alla områden, kolla upp de av användaren angivna
        områdesnamnen. Tar lista med strängar,
        returnerar lista med {Id, Description, Area}."""
    print "Fetching list of all areas..."
    all_areas = load_areas(fetch_areas())
    res = []
    idres = []
    for userarea in userlist:
        try:
            found = next(area for area in all_areas if
                         area["Description"] == userarea)
            res.append(found)
            idres.append(found["Id"])
        except StopIteration:
            print "Error: Couldn't find any match for \"%s\"." % userarea
    if len(res) < len(userlist):
        print "Error: Some given areas couldn't be matched."
    else:
        print "All given areas successfully matched."
    return (res, idres)

def load_config():
    res = {}
    config = ConfigParser.ConfigParser()
    try:
        config.readfp(open('sgskoll.conf'))
    except IOError:
        #TODO: default config
        pass
    with open('desired_areas.conf') as areafile:
        #TODO: default config
        config.set(u"Search Preferences", u"desired_areas",
                   areafile.read().splitlines())
    return config

if __name__ == '__main__':
    print "Loading config..."
    conf = load_config()
    print "Looking up desired areas..."
    areas, area_ids = lookup_areas(conf.get("Search Preferences",
                                            "desired_areas"))
    print "Found the following areas:"
    for area in areas:
        print "%(Id)s: %(Area)s: %(Description)s" % area

    if not os.path.exists('sampledata'):
        print "Downloading search data..."
        with open('sampledata', 'w') as f:
            f.write(fetch_search_data().read())

    data = load_search_data(open('sampledata'))
    print "Found the following matches:"
    filterfn = lambda obj: obj["RentPerMonthSort"] >= int(conf.get("Search Preferences", "min_rent")) and obj["RentPerMonthSort"] <= int(conf.get("Search Preferences", "max_rent")) and obj["ObjectAreaSort"] >= int(conf.get("Search Preferences", "min_area")) and obj["ObjectAreaSort"] <= int(conf.get("Search Preferences", "max_area")) and obj["ObjectSubGroupNo"] in map(int, conf.get("Search Preferences", "apartment_types").split(",")) and obj["SeekAreaNo"] in area_ids

    for obj in ifilter(filterfn, data["Result"]):
        print ("%(Street)s (%(ObjectAreaSort)d kvm, %(RentPerMonthSort)d kr)") % obj



#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import urllib2
import json
import difflib
import ConfigParser
from itertools import ifilter
from functools import partial

AREAS_URL = u'http://marknad.sgsstudentbostader.se/API/Service/SearchServiceHandler.ashx?objectMainGroupNo=1&visibleClient=true&visibleProfile=true&asTree=true&Method=GetSearchAreas'

SEARCH_URL = u'http://marknad.sgsstudentbostader.se/API/Service/SearchServiceHandler.ashx'

ITEMINFO_URL = u'http://marknad.sgsstudentbostader.se/pgObjectInformation.aspx?company=1&obj=%(ObjectNo)s'

SEARCH_PARAMS = {
    u"Parm1": u'{"CompanyNo":1,"SyndicateNo":1,"ObjectMainGroupNo":1,"Advertisements":[{"No":-1}],"RentLimit":{"Min":0,"Max":15000},"AreaLimit":{"Min":0,"Max":150},"Page":1,"Take":10,"SortOrder":"EndPeriodMP asc, CompanyNo asc,SeekAreaDescription asc,StreetName asc","ReturnParameters":["ObjectNo","FirstEstateImageUrl","Street","SeekAreaDescription","PlaceName","ObjectSubDescription","ObjectArea","RentPerMonth","MarketPlaceDescription","CountInterest","FirstInfoTextShort","FirstInfoText","EndPeriodMP","FreeFrom","SeekAreaUrl","Latitude","Longitude","BoardNo"]}',
    u"CallbackMethod": u'PostObjectSearch',
    u"CallbackParmCount": u'1',
    u"__WWEVENTCALLBACK": u'' }

SEARCH_HEADERS = {
    u"Accept": u'application/json,text/*',
    u"X-Momentum-API-KEY": u'u15fJ8yRMCIu////+aEYR7+XJwj1hiE9gIXfoo/eje4=',
    u"X-Requested-With": u'XMLHttpRequest' }

OBJECT_FORMAT = (u"  %(FreeFrom)s - %(Street)s vån. %(ObjectFloor)s " +
                 u"(%(ObjectAreaSort)d kvm, %(RentPerMonthSort)d kr): " +
                 u"%(CountInterest)d interested.")


def fetch_search_data():
    u"""Hämta sökresultat. Returnerar file-like."""
    request = urllib2.Request(SEARCH_URL,
                              urllib.urlencode(SEARCH_PARAMS),
                              SEARCH_HEADERS)
    return urllib2.urlopen(request)

def load_search_data(fp):
    u"""Generöst namngiven metod."""
    data = json.load(fp)
    for obj in data[u"Result"]:
        obj[u"ObjectFloor"] = obj[u"ObjectFloor"].strip()
    return data

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
    if data[u"Childs"] == []:
        return [{u"Id": data[u"Id"],
                 u"Description": data[u"Description"],
                 u"Area": parentname}]
    res = []
    for child in data[u"Childs"]:
        res.extend(get_areas_list(child, data[u"Description"]))
    return res

def lookup_areas(userlist):
    u"""Hämta lista på alla områden, kolla upp de av användaren angivna
        områdesnamnen. Tar lista med strängar,
        returnerar lista med {Id, Description, Area}."""
    print u"Desired areas: "
    for userarea in userlist:
        print u"  " + userarea
    print u"Fetching list of all areas...",
    try:
        areas_fp = fetch_areas()
        print "OK"
    except urllib2.URLError as e:
        sys.stderr.write(u"ERROR: failed fetching list of all areas\n")
        raise
    print u"Matching given areas..."
    all_areas = load_areas(fetch_areas())
    res = []
    idres = []
    matcher = difflib.SequenceMatcher()
    for userarea in userlist:
        best_ratio = 0
        best_match = {}
        matcher.set_seq2(userarea)
        it = iter(all_areas)
        while True:
            try:
                area = it.next()
                matcher.set_seq1(area[u"Description"])
                ratio = matcher.ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = area
                if area[u"Description"] == userarea:
                    res.append(area)
                    idres.append(area[u"Id"])
                    break
            except StopIteration:
                sys.stderr.write((u"  WARNING: Couldn't find any match " +
                                  u"for \"%s\". Did you mean \"%s\"?\n") %
                                  (userarea, best_match[u"Description"]))
                break
    if len(res) < len(userlist):
        sys.stderr.write(u"  WARNING: Some given areas couldn't be matched.\n")
    else:
        print u"OK"
    return (res, idres)

def load_config():
    res = {}
    config = ConfigParser.ConfigParser()
    try:
        config.readfp(open(u'sgskoll.conf'))
    except IOError:
        #TODO: default config
        pass
    with open(u'desired_areas.conf') as areafile:
        #TODO: default config
        config.set(u"Search Preferences", u"desired_areas",
                   map(lambda s: s.decode('utf-8'),
                       areafile.read().splitlines()))
    return config

def load_search_prefs(config):
    res = {}
    for key, val in config.items(u"Search Preferences"):
        res[key] = val
    for key in [u"min_rent",u"max_rent",u"min_area",u"max_area"]:
        res[key] = int(res[key])
    res[u"apartment_types"] = map(int, res[u"apartment_types"].split(u","))
    res[u"areas"], res[u"area_ids"] = lookup_areas(res[u"desired_areas"])
    return res

def filterfn(search_prefs, obj):
    return (obj[u"RentPerMonthSort"] >= search_prefs[u"min_rent"] and
            obj[u"RentPerMonthSort"] <= search_prefs[u"max_rent"] and
            obj[u"ObjectAreaSort"] >= search_prefs[u"min_area"] and
            obj[u"ObjectAreaSort"] <= search_prefs[u"max_area"] and
            obj[u"ObjectSubGroupNo"] in search_prefs[u"apartment_types"] and
            obj[u"SeekAreaNo"] in search_prefs[u"area_ids"])

def obj_format_string(obj):
    area_rent = u"%(ObjectAreaSort)d kvm, %(RentPerMonthSort)d kr"
    for prop in obj[u"Properties"]:
        if prop[u"SyndicatePropertyNo"] == 5: # 10-mån
            area_rent = area_rent + u" [10 mån]"
            break
    return (u"  %(FreeFrom)s - %(Street)s vån. %(ObjectFloor)s " +
            u"(" + area_rent + u"): " +
            u"%(CountInterest)d interested.")


if __name__ == u'__main__':
    print u"Loading config..."
    conf = load_config()
    search_prefs = load_search_prefs(conf)
    print u"Using the following desired areas:"
    for area in search_prefs[u"areas"]:
        print u"  %(Id)s: %(Area)s: %(Description)s" % area
    print (u"Preferences: rent in [%(min_rent)d,%(max_rent)d] kr, " +
           u"area in [%(min_area)d,%(max_area)d] kvm") % search_prefs

    if not os.path.exists(u'sampledata'):
        print u"Downloading search data..."
        with open(u'sampledata', u'w') as f:
            f.write(fetch_search_data().read())
    else:
        print u"Using previously downloaded data..."

    data = load_search_data(open(u'sampledata'))

    print u"" # lol
    print (u"Most wanted is in %(SeekAreaDescription)s:\n" +
           OBJECT_FORMAT) % max(data[u"Result"],
                                key=lambda o: o["CountInterest"])

    print u""
    print u"Found the following matches:"

    for obj in ifilter(partial(filterfn, search_prefs), data[u"Result"]):
        print obj_format_string(obj) % obj
        print u"    " + ITEMINFO_URL % obj



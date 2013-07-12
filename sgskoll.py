#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import urllib.request, urllib.parse, urllib.error
import json
import difflib
import configparser

from functools import partial

AREAS_URL = 'http://marknad.sgsstudentbostader.se/API/Service/SearchServiceHandler.ashx?objectMainGroupNo=1&visibleClient=true&visibleProfile=true&asTree=true&Method=GetSearchAreas'

SEARCH_URL = 'http://marknad.sgsstudentbostader.se/API/Service/SearchServiceHandler.ashx'

ITEMINFO_URL = 'http://marknad.sgsstudentbostader.se/pgObjectInformation.aspx?company=1&obj={ObjectNo}'

SEARCH_PARAMS = {
    "Parm1": '{"CompanyNo":1,"SyndicateNo":1,"ObjectMainGroupNo":1,"Advertisements":[{"No":-1}],"RentLimit":{"Min":0,"Max":15000},"AreaLimit":{"Min":0,"Max":150},"Page":1,"Take":10,"SortOrder":"EndPeriodMP asc, CompanyNo asc,SeekAreaDescription asc,StreetName asc","ReturnParameters":["ObjectNo","FirstEstateImageUrl","Street","SeekAreaDescription","PlaceName","ObjectSubDescription","ObjectArea","RentPerMonth","MarketPlaceDescription","CountInterest","FirstInfoTextShort","FirstInfoText","EndPeriodMP","FreeFrom","SeekAreaUrl","Latitude","Longitude","BoardNo"]}',
    "CallbackMethod": 'PostObjectSearch',
    "CallbackParmCount": '1',
    "__WWEVENTCALLBACK": '' }

SEARCH_HEADERS = {
    "Accept": 'application/json,text/*',
    "X-Momentum-API-KEY": 'u15fJ8yRMCIu////+aEYR7+XJwj1hiE9gIXfoo/eje4=',
    "X-Requested-With": 'XMLHttpRequest' }

OBJECT_FORMAT = "  {FreeFrom} - {Street} vån. {ObjectFloor} " \
                "({ObjectAreaSort} kvm, {RentPerMonthSort} kr): " \
                "{CountInterest} interested."


def fetch_search_data():
    """Hämta sökresultat. Returnerar file-like."""
    request = urllib.request.Request(SEARCH_URL,
                              urllib.parse.urlencode(SEARCH_PARAMS).encode('utf-8'),
                              SEARCH_HEADERS)
    return urllib.request.urlopen(request)

def load_search_data(s):
    """Generöst namngiven metod. Tar en _sträng_"""
    data = json.loads(s)
    for obj in data["Result"]:
        obj["ObjectFloor"] = obj["ObjectFloor"].strip()
    return data

def fetch_areas():
    """Hämta hem lista på områden. Returnerar file-like."""
    request = urllib.request.Request(AREAS_URL, headers=SEARCH_HEADERS)
    return urllib.request.urlopen(request)

def load_areas(s):
    """Gör sans av den mottagna areadatan."""
    # dubbelt escapead json. enterprise!
    return get_areas_list(json.loads(json.loads(s)))

def get_areas_list(data, parentname=''):
    """Omvandla till mindre obtust format."""
    if data["Childs"] == []:
        return [{"Id": data["Id"],
                 "Description": data["Description"],
                 "Area": parentname}]
    res = []
    for child in data["Childs"]:
        res.extend(get_areas_list(child, data["Description"]))
    return res

def lookup_areas(userlist):
    """Hämta lista på alla områden, kolla upp de av användaren angivna
        områdesnamnen. Tar lista med strängar,
        returnerar lista med {Id, Description, Area}."""
    print("Desired areas: ")
    for userarea in userlist:
        print("  " + userarea)
    print("Fetching list of all areas...", end=' ')
    try:
        areas_fp = fetch_areas()
        print("OK")
    except urllib.error.URLError as e:
        sys.stderr.write("ERROR: failed fetching list of all areas\n")
        raise
    print("Matching given areas...")
    all_areas = load_areas(fetch_areas().read().decode('utf-8'))
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
                area = next(it)
                matcher.set_seq1(area["Description"])
                ratio = matcher.ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = area
                if area["Description"] == userarea:
                    res.append(area)
                    idres.append(area["Id"])
                    break
            except StopIteration:
                sys.stderr.write(("  WARNING: Couldn't find any match " \
                                  "for \"{0}\". Did you mean " \
                                  "\"{1[Description]}\"?\n").format(
                                    userarea, best_match))
                break
    if len(res) < len(userlist):
        sys.stderr.write("  WARNING: Some given areas couldn't be matched.\n")
    else:
        print("All areas matched OK")
    return (res, idres)

def load_config():
    res = {}
    config = configparser.ConfigParser()
    try:
        config.readfp(open('sgskoll.conf', encoding='utf-8'))
    except IOError:
        #TODO: default config
        pass

    return config

def load_search_prefs(config):
    res = {}
    for key, val in config.items("Search Preferences"):
        res[key] = val
    for key in ["min_rent","max_rent","min_area","max_area"]:
        res[key] = int(res[key])
    with open('desired_areas.conf', encoding='utf-8') as areafile:
        #TODO: default config, flytta till load_search_prefs
        res["desired_areas"] = []
        for line in areafile.read().splitlines():
            stripped = line.split('#')[0].strip()
            if stripped:
                res["desired_areas"].append(stripped)
    res["apartment_types"] = list(map(int, res["apartment_types"].split(",")))
    res["areas"], res["area_ids"] = lookup_areas(res["desired_areas"])
    return res

def get_matches(search_prefs, data):
    return list(filter(partial(filterfn, search_prefs), data["Result"]))


def filterfn(search_prefs, obj):
    return (obj["RentPerMonthSort"] >= search_prefs["min_rent"] and
            obj["RentPerMonthSort"] <= search_prefs["max_rent"] and
            obj["ObjectAreaSort"] >= search_prefs["min_area"] and
            obj["ObjectAreaSort"] <= search_prefs["max_area"] and
            obj["ObjectSubGroupNo"] in search_prefs["apartment_types"] and
            obj["SeekAreaNo"] in search_prefs["area_ids"])

def obj_format_string(obj):
    area_rent = "{ObjectAreaSort} kvm, {RentPerMonthSort} kr"
    for prop in obj["Properties"]:
        if prop["SyndicatePropertyNo"] == 5: # 10-mån
            area_rent = area_rent + " [10 mån]"
            break
    return "  {FreeFrom} - {Street} vån. {ObjectFloor} " \
           "(" + area_rent + "): " \
           "{CountInterest} interested."


if __name__ == '__main__':
    print("Loading config...")
    conf = load_config()
    search_prefs = load_search_prefs(conf)
    print("Using the following desired areas:")
    for area in search_prefs["areas"]:
        print("  {Id}: {Area}: {Description}".format(**area))
    print("Preferences: rent in [{min_rent},{max_rent}] kr, " \
          "area in [{min_area},{max_area}] kvm".format(**search_prefs))

    if not os.path.exists('sampledata'):
        print("Downloading search data...")
        with open('sampledata', 'wb') as f:
            f.write(fetch_search_data().read())
    else:
        print("Using previously downloaded data...")

    data = load_search_data(open('sampledata', encoding='utf-8').read())

    print("") # lol

    most_wanted = max(data["Result"], key=lambda o: o["CountInterest"])
    print(("Most wanted is at {SeekAreaDescription}:\n" +
           OBJECT_FORMAT).format(**most_wanted))
    print("    " + ITEMINFO_URL.format(**most_wanted))

    results = get_matches(search_prefs, data)

    print("")
    if not results:
        print("No matches were found. Maybe you have too high standards.")
    else:
        print("Found the following matches:")
        for obj in results:
            print(obj_format_string(obj).format(**obj))
            print("    " + ITEMINFO_URL.format(**obj))



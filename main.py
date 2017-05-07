#!/usr/bin/env python

import argparse
import os.path
import urllib
import urllib2
import json
from settings import config


def url_safe(str):
    return urllib.quote(str)


def fetch_data(url):
    try:
        response = urllib2.urlopen(url)
        raw = response.read()
        response.close()
        return json.loads(raw)
    except Exception:
        print('Unable to connect to server')


def geocode(location):
    url = config['location-url'].format(loc=url_safe(location))
    data = fetch_data(url)
    if data['status'] == 'ZERO_RESULTS':
        print('Address not found')
    else:
        return data['results'][0]


def weather(latitude, longitude):
    url = config['weather-url'].format(
        key=config['weather-key'],
        lat=latitude,
        lng=longitude
    )
    return fetch_data(url)


def parse_address(address):
    data = ''
    for word in address:
        data += ' ' + word
    return data.strip()


def set_default(location):
    with open(config['save-file'], 'w') as f:
        f.write(str(location))


def get_default():
    if not os.path.exists(config['save-file']):
        return
    with open(config['save-file'], 'r') as f:
        loc = f.read()
    return loc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("address",
                        help="The address, city or post code for the weather.",
                        nargs='*', type=str)

    parser.add_argument("-l", "--list",
                        help="displays the default location",
                        action="store_true")

    parser.add_argument("-d", "--default",
                        help="saves location as the default and exits",
                        action="store_true")

    parser.add_argument("-s", "--save",
                        help="saves location as the default and fetches weather",
                        action="store_true")

    args = parser.parse_args()

    if args.list:
        print('Default location: {}'.format(get_default()))
        return

    if args.address:
        address = parse_address(args.address)
    else:
        address = get_default()

    if not address:
        print("No default location set.\nPlease run again and include a location.")
        return

    geo = geocode(address)
    if not geo:
        return

    if args.default:
        if args.address:
            set_default(geo['formatted_address'])
            print('Setting {} as default location'.format(geo['formatted_address']))
        else:
            print('No location specified')
        return

    if args.save:
        if args.address:
            set_default(geo['formatted_address'])
            print('Saving {} as default location'.format(geo['formatted_address']))
        else:
            print('No location specified')
            return

    lat = geo['geometry']['location']['lat']
    lng = geo['geometry']['location']['lng']

    data = weather(lat, lng)

    print('')
    print(u'Location : {}'.format(geo['formatted_address']))
    print(u'Weather  : {}'.format(data['currently']['summary']))
    print(u'Currently: {}\xb0C'.format(int(data['currently']['temperature'])))
    print(u'Forecast : {}'.format(data['daily']['summary']))


if __name__ == '__main__':
    main()

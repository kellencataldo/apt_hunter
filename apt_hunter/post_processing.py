import math
import logging

import http_request


class Geolocation():
    def __init__(self, address, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.address = address


def haversine_distance(geo_one, geo_two):
        # https://nathanrooy.github.io/posts/2016-09-07/haversine-with-python/
        radius = 6371000

        phi_one = math.radians(geo_one.latitude)
        phi_two = math.radians(geo_two.latitude)

        delta_phi = math.radians(geo_two.latitude - geo_one.latitude)
        delta_lambda = math.radians(geo_two.longitude - geo_one.longitude)

        a = math.sin(delta_phi/2.0)**2 + math.cos(phi_one) * math.cos(phi_two) * math.sin(delta_lambda/2.0)**2
        c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))

        return radius * c * 0.000621371      # output distance in miles


def address_to_geo(address, google_api_key):
    sanitized_address = address.replace(' ', '+')
    request_prefix = 'https://maps.googleapis.com/maps/api/geocode/json?'
    request_url = f'{request_prefix}address={sanitized_address}&key={google_api_key}'
    json_result = http_request.json_request(request_url)
    geo_blob = json_result['results'][0]['geometry']['location']
    return Geolocation(address, geo_blob['lat'], geo_blob['lng'])


def get_closest(apt_geo, category, geo_list):
    closest_item = geo_list[0]
    closest_dist = haversine_distance(apt_geo, closest_item)
    if len(geo_list) == 1:
        return f'DISTANCE TO {category} AT ADDRESS {closest_item.address}: {closest_dist:.2f} MILES EUCLIDEAN'
    for geolocation in geo_list:
        compare_dist = haversine_distance(apt_geo, geolocation)
        if compare_dist < closest_dist:
            closest_dist = compare_dist
            closest_item = geolocation
    return f'CLOSEST {category} IS {closest_item.address}: {closest_dist:.2f} MILES EUCLIDEAN'


def post_process_entries(apt_entries, post_processing_blob):
    if 'google_maps' not in post_processing_blob or 'addresses' not in post_processing_blob['google_maps']:
        logging.info('No post-processing to be done, skipping')
        return
    import SECRETS
    google_api_key = SECRETS.GOOGLE_API_KEY
    google_maps_blob = post_processing_blob['google_maps']
    address_dict = google_maps_blob['addresses']
    geo_dict = {category: [address_to_geo(address, google_api_key) for address in addresses]
                for category, addresses, in address_dict.items()}
    for i in range(len(apt_entries)):
        apt_geo = address_to_geo(apt_entries[i].address, google_api_key)
        post = '\n'.join(get_closest(apt_geo, category, geo_list) for category, geo_list in geo_dict.items())
        apt_entries[i].post_text = post

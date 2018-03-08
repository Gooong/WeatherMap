import json
import threading
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request

from utils.crawl_weather import refresh_weather, updating_weather
from utils.geojson_reader import read_geojson, get_search_dic

app = Flask(__name__)
china = None
name_object_dict ={}
executor = ThreadPoolExecutor(1)


@app.route('/')
def index():
    return app.send_static_file('weather.html')


@app.route('/<place>')
def hello_world(place):
    return 'Hello World'+place


@app.route('/geojson/search')
def search_place():
    place_name = request.args.get('name')
    if place_name:
        place_name = place_name.strip().lower()
        if place_name in name_object_dict.keys():
            return json.dumps(name_object_dict[place_name].data)
    return  json.dumps("")


@app.route('/geojson/<int:country_id>')
def get_country_geojson(country_id):
    return china.get_sub_geojson([country_id])


@app.route('/geojson/<int:country_id>/<int:sheng_id>')
def get_sheng_geojson(country_id,sheng_id):
    return china.get_sub_geojson([country_id,sheng_id])


@app.route('/geojson/<int:country_id>/<int:sheng_id>/<int:shi_id>')
def get_shi_geojson(country_id,sheng_id,shi_id):
    return china.get_sub_geojson([country_id,sheng_id,shi_id])



if __name__ =='__main__':

    china = read_geojson()
    name_object_dict = get_search_dic(china)
    refresh_weather(china)

    threading.Thread(target=updating_weather, args=[china]).start()
    app.debug = True
    app.run("0.0.0.0",port=80,threaded = True)

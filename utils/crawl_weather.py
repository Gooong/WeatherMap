import time
import xml.etree.ElementTree as ET

import requests

url ="http://flash.weather.com.cn/wmaps/xml/"
count = 0

def fetch_weather(pyName):
    try:
        response = requests.get(url + pyName + '.xml',)
        response.encoding = 'utf8'
        tree = ET.fromstring(response.text)
        time.sleep(0.1)
        return ET.fromstring(response.text)
    except:
        print("connection_error")
        return []



def refresh_weather(china):
    print("refresh_weather")
    global count
    china.eTree = fetch_weather(china.name)

    print("---省---")
    for sheng in china.eTree:
        sheng_name = sheng.attrib['pyName']
        sheng_place = china.get_from_name(sheng_name) #通过拼音能匹配上
        if sheng_place:
            sheng_place.data['properties'].update(sheng.attrib)
            sheng_place.hasWeather = True
        else:
            #print(sheng_name)
            pass
        #print(sheng.attrib)

    print("---市---")
    for sheng in china.eTree:
        sheng_name = sheng.attrib['pyName']
        if sheng_name in{'beijing','shanghai','tianjin','chongqing'}:
            continue

        sheng_place = china.get_from_name(sheng_name)
        if sheng_place:
            sheng_place.eTree = fetch_weather(sheng_name)
            for shi in sheng_place.eTree:
                shi_name = shi.attrib['pyName']
                shi_place = sheng_place.get_from_name(shi_name)
                if not shi_place:
                    shi_chinese_name = shi.attrib['cityname']
                    for shi_of_sheng in sheng_place.sub.values():
                        if shi_of_sheng.chinese_name.find(shi_chinese_name) != -1:
                            shi_place = shi_of_sheng    #拼音不匹配，通过汉字匹配上了
                            shi_place.name = shi_name   #修改原来的拼音，后面要根据名字来取天气，市的key和市的name可能不一样了
                            break
                if shi_place:
                    shi_place.data['properties'].update(shi.attrib)
                    shi_place.hasWeather = True
                else:
                    pass
                    #print(sheng_name+"::"+shi_name)
                    #shi.id = None   #匹配不上，相当于无用

    print("---县---")
    for sheng in china.sub.values():
        if sheng.name == 'hainan':
            continue
        for shi in sheng.sub.values():
            if(shi.hasWeather):
                shi.eTree = fetch_weather(shi.name)
                for xian in shi.eTree:
                    xian_name = xian.attrib['cityname'].split('县')[0] #天气里的县名
                    xian_place = None
                    for xian_of_shi in shi.sub.keys():
                        if xian_of_shi.find(xian_name) != -1:
                            xian_place = shi.sub[xian_of_shi]
                            break
                    if not xian_place:
                        if xian_name[-1] == '市':
                            for xian_of_shi in shi.sub.values():
                                #print(xian_of_shi.data['properties']['ENGTYPE_3']+"=="+xian_of_shi.data['properties']['NL_NAME_3']+"==")
                                #县的拼音和市的拼音一样，且县的名字为空
                                if xian_of_shi.data['properties']['NAME_3'] == shi.data['properties']['NAME_2'] :
                                    xian_of_shi.data['properties']['NL_NAME_3'] = shi.data['properties']['NL_NAME_2']#县属性改名
                                    xian_place = xian_of_shi
                                    #print("useful")
                                    break
                    if xian_place:
                        xian_place.data['properties'].update(xian.attrib)
                        xian_place.hasWeather = True
                        #count = count +1
                    else:
                        pass
                        #print(sheng.name+"::"+shi.chinese_name+"::"+xian_name)
    print("refresh_weather_done")


def updating_weather(china):
    while True:
        refresh_weather(china)
        time.sleep(60*5)


#print(count)
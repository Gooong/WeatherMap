import json

class PlaceWeather(object):
    def __init__(self,name,id,data,chinese_name):
        self.name = name    #地名,用于和天气数据匹配
        self.chinese_name = chinese_name    #汉字名
        self.id = id
        self.data = data    #该地的属性，天气以及要素数据,存的就是一个Feature
        self.sub = dict()    #该地的附属地区
        self.eTree = None   #xml树
        self.hasWeather = False

    def add(self,name,id,data,chinese_name):
        self.sub[name] = PlaceWeather(name,id,data,chinese_name)

    def get(self,id):       #通过ID查附属，最可靠
        for place in self.sub.values():
            if place.id == id:
                return  place
        return None

    def get_from_name(self,name):   #通过名字查附属，不太可靠
        return self.sub.get(name)

    def get_sub_geojson(self,id_list):
        temp_palce = None
        if(id_list):
            if id_list[0] == self.id:
                temp_palce = self
                for id in id_list[1:]:
                    temp_palce = temp_palce.get(id) #最终指向查询的节点
        #打包它子节点的信息
        sub_datas =json.loads('{"type":"FeatureCollection","features":[]}')
        if(temp_palce):
            for sub in temp_palce.sub.values():
                sub_datas['features'].append(sub.data)

        return json.dumps(sub_datas)

def read_geojson():
    print("ReadGeoJson")
    sheng_f = open("geo_files/sheng.json",'r',encoding='utf8')
    shi_f = open("geo_files/shi.json",'r',encoding='utf8')
    xian_f = open("geo_files/xian.json",'r',encoding='utf8')
    sheng_collection = json.load(sheng_f)
    #print(sheng_collection['features'][6])

    china = PlaceWeather('china',1,[],"中国")    #数据根节点
    for province in sheng_collection['features']:
        name = province['properties']['NAME_1'].lower()
        id = province['properties']['ID_1']
        chinese_name = province['properties']['NL_NAME_1']
        china.add(name,id,province,chinese_name)

    shi_collection = json.load(shi_f)
    #print(shi_collection['features'][0])
    for shi in shi_collection['features']:
        sheng_id =  shi['properties']['ID_1']
        name = shi['properties']['NAME_2'].lower()
        chinese_name = shi['properties']['NL_NAME_2']
        id = shi['properties']['ID_2']
        try:
            china.get(sheng_id).add(name,id,shi,chinese_name)
        except:
            pass
            #print(shi)


    xian_collection = json.load(xian_f)
    for xian in xian_collection['features']:
        sheng_id = xian['properties']['ID_1']
        shi_id = xian['properties']['ID_2']
        xian_id = xian['properties']['ID_3']
        name = xian['properties']['NL_NAME_3']
        chinese_name = xian['properties']['NL_NAME_3']
        try:
            china.get(sheng_id).get(shi_id).add(name,xian_id,xian,chinese_name)
        except:
            pass
            #print(xian)

    sheng_f.close()
    shi_f.close()
    xian_f.close()

    return china

def get_search_dic(china):
    name_object_dict ={}
    for sheng_name in china.sub.keys():
        sheng_data = china.sub[sheng_name]
        sheng_name1 = sheng_data.data['properties'].get('NAME_1').lower()
        sheng_name2 = sheng_data.data['properties'].get('NL_NAME_1')
        sheng_name3 = sheng_data.data['properties'].get('NAME').lower()
        name_object_dict[sheng_name] = sheng_data
        name_object_dict[sheng_name1] = sheng_data
        name_object_dict[sheng_name2] = sheng_data
        name_object_dict[sheng_name3] = sheng_data

        for shi_name in sheng_data.sub.keys():
            shi_data = sheng_data.sub[shi_name]
            shi_name1 = shi_data.data['properties'].get('NAME_2').lower()
            shi_name2 = shi_data.data['properties'].get('NL_NAME_2').split('|')[0]
            shi_name3 = shi_name2.split('市')[0]
            name_object_dict[shi_name] = shi_data
            name_object_dict[shi_name1] = shi_data
            name_object_dict[shi_name2] = shi_data
            name_object_dict[shi_name3] = shi_data

            for xian_name in shi_data.sub.keys():
                xian_data = shi_data.sub[xian_name]
                xian_name1 = xian_data.data['properties'].get('NAME_3').lower()
                xian_name2 = xian_data.data['properties'].get('NL_NAME_3').split('|')[0]
                xian_name3= xian_name2.split('县')[0]
                name_object_dict[xian_name] = xian_data
                name_object_dict[xian_name1] = xian_data
                name_object_dict[xian_name2] = xian_data
                name_object_dict[xian_name3] = xian_data


    return  name_object_dict
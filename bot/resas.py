# -*- coding: utf-8 -*-
import json
import requests

#resas key 
resas_key = 'HLg5C8mn9xIk86rmvCg9T8XogMsQ5oSdPlZp5Rcz'

#参照データ情報
year = '2015' #対象年
pref_code = '11'
region_code = '1' #地域コード
country_code = '103'#国コード
purpose = '1'#目的　１：全て　２：観光
month = '04' #訪問月
pot = '1' #訪問時間帯　１：昼　２：夜

def get_resas(key,url):
    x = json.loads(requests.get('https://opendata.resas-portal.go.jp/' + url, headers={'X-API-KEY':key}).text)
    #x_json = json.dumps(x, ensure_ascii=False, indent=4)
    #groupDict = x['result']
    #nameList = groupDict.keys()
    #print(groupDict)
    
    
    ##dict, str
    #print(type(x))
    #print(type(x_json))
    
    #print(x_json)
    
    print(x['message'],x['result'])
    #return(type(x['result']['data'][0]['lat']))
    
if __name__ == "__main__" :
    #国籍毎のよく行く目的地
    get_resas(resas_key,'api/v1/tourism/foreigners/forTo?year='+year
              +'&prefCode='+pref_code
              +'&regionCode='+region_code
              +'&countryCode='+country_code
              +'&purpose='+purpose)
    #目的地によく来る国籍の人
    get_resas(resas_key,'api/v1/tourism/foreigners/forFrom?purpose='+purpose
              +'&year='+year
              +'&prefCode='+pref_code)
    #季節毎の訪日外国人数
    get_resas(resas_key,'api/v1/partner/docomo/inbound?year='+year
              +'&month='+month
              +'&prefCode='+pref_code
              +'&periodOfTime='+pot)
    #観光スポット
    get_resas(resas_key,'api/v1/tourism/attractions?prefCode='+pref_code+'&cityCode=-')
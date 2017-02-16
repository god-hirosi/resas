# -*- coding: utf-8 -*-
import json
import requests
import pandas as pd
from pandas import DataFrame


#resas key 
resas_key = 'HLg5C8mn9xIk86rmvCg9T8XogMsQ5oSdPlZp5Rcz'

#参照データ情報
year = '2015' #対象年
quarter = '2' #対象クウォーター
#pref_code = '11'
region_code = '1' #地域コード
#country_code = '103'#国コード
purpose = '1'#目的　１：全て　２：観光
month = '04' #訪問月
pot = '1' #訪問時間帯　１：昼　２：夜


##############################
## 関数作成エリア
##############################

def get_resas(key,url):
    x = json.loads(requests.get('https://opendata.resas-portal.go.jp/' + url, headers={'X-API-KEY':key}).text)
    #print (x['message'],x['result'])
    #print x['result']
    return x['result']
    #return(type(x['result']['data'][0]['lat']))
    
# 国籍コードを入れると、よく行く都道府県のコードを返す
def get_Pref_fromNation(key,url):
    x = json.loads(requests.get('https://opendata.resas-portal.go.jp/' + url, headers={'X-API-KEY':key}).text)
    return x['result']
    
# 都道府県コードを入れると、よく訪問する国籍のコードを返す
def get_Nation_fromPref(key,url):
    x = json.loads(requests.get('https://opendata.resas-portal.go.jp/' + url, headers={'X-API-KEY':key}).text)
    return x['result']

# 都道府県コード、月、を入れると、その月の訪日外国人人数を返す
def get_VisitNum(key,url):
    x = json.loads(requests.get('https://opendata.resas-portal.go.jp/' + url, headers={'X-API-KEY':key}).text)
    return x['result']

# 都道府県コードを入れると、日本人がよく行く観光スポット名を返す
def get_Spot(key,url):
    x = json.loads(requests.get('https://opendata.resas-portal.go.jp/' + url, headers={'X-API-KEY':key}).text)
    return x['result']

# 国籍のコード変換
def get_nationCd(in_nation):
    return int(countryList.loc[(CountryList.countryName == in_nation), 'countryCd'])

# 都道府県のコード変換
def get_prefCd(in_pref):
    return int(prefList.loc[(prefList.prefName == in_pref), 'prefCd'])



##############################
## メイン関数
##############################

# 初期設定
in_nation = "大韓民国"
countryList = pd.read_csv("CountryList.csv", names = ('regionCd', 'regionName', 'countryCd', 'countryName'))
in_pref = "京都府"
prefList = pd.read_csv("PrefExchangeList.csv", names = ('prefName', 'shortName', 'prefCd'))


### 処理１：国籍を入れると、よく行く都道府県コードを取得 ###
#
# 国籍をコード化
nationCd1 = get_nationCd(in_nation)
print "国籍：%s、コード：%d" %(in_nation, nationCd1)
#
# 国籍コードから人気の都道府県コードを2件取得：（pref1, pref2） #※アメリカ合衆国：東京都、などない場合もある。その場合は、0を返す。
pref1 = 0
pref2 = 0
tmp_pref1, tmp_value1 = 0, 0
tmp_pref2, tmp_value2 = 1, 1
i = 1
while i < 48:
    pref =  get_Pref_fromNation(resas_key,'api/v1/tourism/foreigners/forTo?year='+year
                +'&prefCode='+str(i)   
                +'&regionCode='+region_code
                +'&countryCode='+str(nationCd1)
                +'&purpose='+purpose)
    #print str(pref)
    if str(pref) == 'None':
        i += 1
        continue
    n = 0
    j = 0
    while j < len(pref['changes'][0]['data']):
        if (pref['changes'][0]['data'][j]['year'] == int(year)) and (pref['changes'][0]['data'][j]['quarter'] == int(quarter)):
            n = int(pref['changes'][0]['data'][j]['value'])
        j += 1        
    if n > tmp_value2:
        tmp_value1 = tmp_value2
        tmp_pref1 = tmp_pref2
        tmp_value2 = n
        tmp_pref2 = int(pref['changes'][0]['prefCode'])
    else:
        if n > tmp_value1:
            tmp_value1 = n
            tmp_pref1 = int(pref['changes'][0]['prefCode'])
    i += 1
pref1, pref2 = tmp_pref1, tmp_pref2
#
print "国籍：%s がよく行く都道府県コード：%d, %d" %(in_nation, pref1, pref2)


### 処理2：都道府県を入れると、そこに人気ある国籍の人がよく行く都道府県コードを取得 ###
#
# 都道府県をコード化
prefCd = get_prefCd(in_pref)
print "都道府県：%s、コード：%d" %(in_pref, prefCd)
#
# 都道府県コードから人気の国籍コードを2件取得: (nation1, nation2)
nation = get_Nation_fromPref(resas_key,'api/v1/tourism/foreigners/forFrom?purpose='+purpose
              +'&year='+year
              +'&prefCode='+pref_code)
nationCd3, nationCd4 = 0, 0
tmp_nation1, tmp_value1 = 0, 0
tmp_nation2, tmp_value2 = 1, 1
i = 0
j = 0
n = 0
while i < len(nation['changes']):
    while j < len(nation['changes'][i]['data']):
        if (int(nation['changes'][i]['data'][j]['year']) == int(year)) and (int(nation['changes'][i]['data'][j]['quarter']) == int(quarter)):
            n = nation['changes'][i]['data'][j]['value']
            #print n
        j += 1
    if n > tmp_value2:
        tmp_value1 = tmp_value2
        tmp_nation1 = tmp_nation2
        tmp_value2 = n
        tmp_nation2 = int(nation['changes'][i]['countryCode'])
    elif n > tmp_value1:
        tmp_value1 = n
        tmp_nation1 = int(nation['changes'][i]['countryCode'])
    i += 1
    j = 0
nationCd3, nationCd4 = tmp_nation1, tmp_nation2
print "都道府県：%s によく行く国籍：%s, %s" %(in_pref, str(nationCd3), str(nationCd4))
#
# 国籍コードからよく行く都道府県コードを取得（＝処理1）
pref3, pref4 = 0, 0
pref5, pref6 = 0, 0
tmp_pref1, tmp_value1 = 0, 0
tmp_pref2, tmp_value2 = 1, 1
x = 0
for nationId in (nationCd3, nationCd4):
    i = 1
    while i < 48:
        pref =  get_Pref_fromNation(resas_key,'api/v1/tourism/foreigners/forTo?year='+year
                    +'&prefCode='+str(i)   
                    +'&regionCode='+region_code
                    +'&countryCode='+str(nationCd)
                    +'&purpose='+purpose)
        #print str(pref)
        if str(pref) == 'None':
            i += 1
            continue
        n = 0
        j = 0
        while j < len(pref['changes'][0]['data']):
            if (pref['changes'][0]['data'][j]['year'] == int(year)) and (pref['changes'][0]['data'][j]['quarter'] == int(quarter)):
                n = int(pref['changes'][0]['data'][j]['value'])
            j += 1
        if n > tmp_value2:
            tmp_value1 = tmp_value2
            tmp_pref1 = tmp_pref2
            tmp_value2 = n
            tmp_pref2 = int(pref['changes'][0]['prefCode'])
        else:
            if n > tmp_value1:
                tmp_value1 = n
                tmp_pref1 = int(pref['changes'][0]['prefCode'])
        i += 1    
    if x == 0:
        pref3, pref4 = tmp_pref1, tmp_pref2
    elif x == 1:
        pref5, pref6 = tmp_pref1, tmp_pref2
    tmp_pref1, tmp_value1 = 0, 0
    tmp_pref2, tmp_value2 = 1, 1
    x += 1
#
print "国籍コード：%s がよく行く都道府県コード：%s, %s\国籍コード：%s がよく行く都道府県コード：%s, %s" %(str(nationCd3), str(pref3), str(pref4), str(nationCd4), str(pref5), str(pref6))
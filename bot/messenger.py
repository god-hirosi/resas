# -*- coding: utf-8 -*-

import logging
import random
import requests
import pandas as pd
from pandas import DataFrame

logger = logging.getLogger(__name__)

# 国籍と都道府県の名前とコード変換リストを読み込み
countryList = pd.read_csv("data/CountryList.csv", names = ('regionCd', 'regionName', 'countryCd', 'countryName'))
prefList = pd.read_csv("data/PrefExchangeList.csv", names = ('prefName', 'shortName', 'prefCd'))

#参照データ情報
year = '2015' #対象年
quarter = '2' #対象クウォーター
#pref_code = '11'
region_code = '1' #地域コード
#country_code = '103'#国コード
purpose = '1'#目的　１：全て　２：観光
month = '04' #訪問月
pot = '1' #訪問時間帯　１：昼　２：夜


class Messenger(object):
    def __init__(self, slack_clients):
        self.clients = slack_clients

    def send_message(self, channel_id, msg):
        # in the case of Group and Private channels, RTM channel payload is a complex dictionary
        if isinstance(channel_id, dict):
            channel_id = channel_id['id']
        logger.debug('Sending msg: %s to channel: %s' % (msg, channel_id))
        channel = self.clients.rtm.server.channels.find(channel_id)
        channel.send_message(msg)

    def write_help_message(self, channel_id):
        bot_uid = self.clients.bot_user_id()
        txt = '{}\n{}\n{}\n{}'.format(
            "I'm your friendly Slack bot written in Python.  I'll *_respond_* to the following commands:",
            "> `hi <@" + bot_uid + ">` - I'll respond with a randomized greeting mentioning your user. :wave:",
            "> `<@" + bot_uid + "> joke` - I'll tell you one of my finest jokes, with a typing pause for effect. :laughing:",
            "> `<@" + bot_uid + "> attachment` - I'll demo a post with an attachment using the Web API. :paperclip:")
        self.send_message(channel_id, txt)

    def write_greeting(self, channel_id, user_id):
        greetings = ['Hi', 'Hello', 'Nice to meet you', 'Howdy', 'Salutations']
        txt = '{}, <@{}>!'.format(random.choice(greetings), user_id)
        self.send_message(channel_id, txt)

    def write_prompt(self, channel_id):
        bot_uid = self.clients.bot_user_id()
        txt = "I'm sorry, I didn't quite understand... Can I help you? (e.g. `<@" + bot_uid + "> help`)"
        self.send_message(channel_id, txt)

    def write_joke(self, channel_id):
        question = "Why did the python cross the road?"
        self.send_message(channel_id, question)
        self.clients.send_user_typing_pause(channel_id)
        answer = "To eat the chicken on the other side! :laughing:"
        self.send_message(channel_id, answer)


    def write_error(self, channel_id, err_msg):
        txt = ":face_with_head_bandage: my maker didn't handle this error very well:\n>```{}```".format(err_msg)
        self.send_message(channel_id, txt)

    def demo_attachment(self, channel_id):
        txt = "Beep Beep Boop is a ridiculously simple hosting platform for your Slackbots."
        attachment = {
            "pretext": "We bring bots to life. :sunglasses: :thumbsup:",
            "title": "Host, deploy and share your bot in seconds.",
            "title_link": "https://beepboophq.com/",
            "text": txt,
            "fallback": txt,
            "image_url": "https://storage.googleapis.com/beepboophq/_assets/bot-1.22f6fb.png",
            "color": "#7CD197",
        }
        self.clients.web.chat.post_message(channel_id, txt, attachments=[attachment], as_user='true')
        
    ##############################
    ## 新規作成関数エリア
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
        return int(countryList.loc[(countryList.countryName == in_nation), 'countryCd'])

    # 都道府県のコード変換
    def get_prefCd(in_pref):
        return int(prefList.loc[(prefList.prefName == in_pref), 'prefCd'])

    # 国籍から都道府県Top2のコードを取得
    def get_PrefTop2_fromNation(in_nation):
        # 国籍をコード化
        nationCd1 = get_nationCd(in_nation)
        print "国籍：%s、コード：%d" %(in_nation, nationCd1)
        #
        # 国籍コードから人気の都道府県コードを2件取得：（pref1, pref2） #※アメリカ合衆国：東京都、などない場合もある。その場合は、0を返す。
        tmp_pref1, tmp_value1 = 0, 0
        tmp_pref2, tmp_value2 = 1, 1
        i = 1
        while i < 48:
            print i
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
        return tmp_pref1, tmp_pref2
    
    # 都道府県から人気な国籍Top2のコードを取得
    def get_NationTop2_fromPref(in_pref):
        # 都道府県をコード化
        prefCd = get_prefCd(in_pref)
        print "都道府県：%s、コード：%d" %(in_pref, prefCd)
        #
        # 都道府県コードから人気の国籍コードを2件取得: (nation1, nation2)
        nation = get_Nation_fromPref(resas_key,'api/v1/tourism/foreigners/forFrom?purpose='+purpose
                      +'&year='+year
                      +'&prefCode='+pref_code)
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
        return tmp_nation1, tmp_nation2
    
    # 都道府県コードから食べログで和食・日本料理の検索結果URLを返す
    def get_taberogu_url(prefCdList):
        url_tabe_list = []
        for pref_ in prefCdList:
            if (pref_ not in url_tabe_list) and str(pref_) != '0':
                url_tabe_list.append(str(pref_))
        i = 0
        while i < len(url_tabe_list):
            pref_short = str(prefList[prefList['prefCd'].str.contains(str(url_tabe_list[i]))]['shortName'])
            url = 'https://tabelog.com/' + pref_short + '/rstLst/lunch/washoku/?sort_mode=1' + \
                '&sw=%E6%97%A5%E6%9C%AC%E6%96%99%E7%90%86&sk=' +\
                '%E5%92%8C%E9%A3%9F%20%E6%97%A5%E6%9C%AC%E6%96%99%' + \
                'E7%90%86%20%E3%83%A9%E3%83%B3%E3%83%81&svd=&svt=&svps=2'            
            url_tabe_list[i] = str(url)
            i += 1
        return url_tabe_list
    
    #  都道府県コードから、あそびゅーで検索結果のURLを返す
    def get_asoview_url(prefCdList):
        url_aso_list = []
        for pref_ in prefCdList:
            if (pref_ not in url_aso_list) and str(pref_) != '0':
                url_aso_list.append(str(pref_))
        i = 0
        while i < len(url_aso_list):
            pref_name = str(prefList[prefList['prefCd'].str.contains(str(url_aso_list[i]))]['prefName'])
            # 以下、主要パラメータ
            # np=人数(int)
            # q=都道府県
            # targetAge=対象年齢(int)
            # tg=24~28 (int, 24:オールシーズン、 25:春、26:夏、27:秋、28:冬)、複数掛け合わせOK
            # timeRequired=所要時間(int) (分)
            # ct=ジャンル(int) (添付写真の上から1〜。ex)7:観光・レジャー )
            url = 'http://www.asoview.com/search/?ymd=&rg=&ct=7&ac=&np=&q=' + pref_name + \
                '&bd=&targetAge=18&timeRequired=180&tg=24&tg=25&tg=26&tg=27&tg=28'
            url_aso_list[i] = str(url)
            i += 1
        return url_aso_list
    
    
    
    
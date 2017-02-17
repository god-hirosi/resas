# -*- coding: utf-8 -*-
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
import json
import logging
import re
import requests
import csv
#import pandas as pd
#from pandas import DataFrame

logger = logging.getLogger(__name__)

# 国籍と都道府県の名前とコード変換リストを読み込み
#countryList = pd.read_csv("data/CountryList.csv", names = ('regionCd', 'regionName', 'countryCd', 'countryName'))
#prefList = pd.read_csv("data/PrefExchangeList.csv", names = ('prefName', 'shortName', 'prefCd'))

# 国籍コード
C_c2n = {}
C_n2c = {}
with open('bot/data/CountryList.csv') as f:
    f.readline()
    rs = csv.reader(f)
    for r in rs:
        c = r[2]
        n = r[3]
        C_c2n[c] = n
        C_n2c[n] = c

# 都道府県コード
P_c2n = {}
P_n2c = {}
with open('bot/data/PrefExchangeList.csv') as f:
    f.readline()
    rs = csv.reader(f)
    for r in rs:
        c = r[1]
        n = r[2]
        P_c2n[c] = n
        P_n2c[n] = c

inp = None
prefs = []
purp_g = False
purp_r = False


class RtmEventHandler(object):
    def __init__(self, slack_clients, msg_writer):
        self.clients = slack_clients
        self.msg_writer = msg_writer

        
    def handle(self, event):

        if 'type' in event:
            self._handle_by_type(event['type'], event)
            
            
    def get_PrefTop2_fromNation(self, nations):
        #if in_nation not in P_n2c:
        cand = []
        for nation in nations:
            countryCode = C_n2c[nation]
            res = c2p[countryCode]
            count = 0
            for p, v in sorted(res.items(), key=lambda x: x[1], reverse=True):
                cand.append([p, v])
                count += 1
                if count == 2:
                    break
        count = 0
        prefs = {}
        for p, v in sorted(cand.items(), key=lambda x: x[1], reverse=True):
            if p in prefs:
                continue
            prefs[p] = v
            count += 1
            if count == 2:
                break
        return prefs
   

    def get_NationTop2_fromPref(self, pref):
        prefCode = P_k2c[pref]
        res = p2c[prefCode]
        count = 0
        cand = []
        for p, v in sorted(res.items(), key=lambda x: x[1], reverse=True):
            cand.append(p)
            count += 1
            if count == 2:
                break
        return cand
    
    def initialize_param(self):
        inp = None
        prefs = []
        purp_g = False
        purp_r = False
        
    
    def suggest(self, inp, prefs, purp_g, purp_r):
        if purp_g:
            url_tabe_list = self.get_taberogu_url(inp, purp_g, prefs, event['channel'])
            url_aso_list = self.get_asoview_url(inp, purp_r, prefs, event['channel'])
            initialize_param()
            continue            
            
        elif purp_r:
            url_aso_list = self.get_asoview_url(inp, purp_r, prefs, event['channel'])
            url_tabe_list = self.get_taberogu_url(inp, purp_g, prefs, event['channel'])
            initialize_param()
            continue            
        
        self.msg_writer.purpose_check(event['channel'])
    
    def _handle_by_type(self, event_type, event):
        # See https://api.slack.com/rtm for a full list of events
        if event_type == 'error':
            # error
            self.msg_writer.write_error(event['channel'], json.dumps(event))
        elif event_type == 'message':
            # message was sent to channel
            self._handle_message(event)
        elif event_type == 'channel_joined':
            # you joined a channel
            self.msg_writer.write_help_message(event['channel'])
        elif event_type == 'group_joined':
            # you joined a private group
            self.msg_writer.write_help_message(event['channel'])
        else:
            pass

    def _handle_message(self, event):
        # Filter out messages from the bot itself, and from non-users (eg. webhooks)
        if ('user' in event) and (not self.clients.is_message_from_me(event['user'])):

            msg_txt = event['text']
            #print msg_txt
            msg_txt = msg_txt.encode('utf-8')

            if self.clients.is_bot_mention(msg_txt) or self._is_direct_message(event['channel']):
                # e.g. user typed: "@pybot tell me a joke!"
                if 'help' in msg_txt:
                    self.msg_writer.write_help_message(event['channel'])
                elif re.search('hi|hey|hello|howdy', msg_txt):
                    self.msg_writer.write_greeting(event['channel'], event['user'])
                elif 'joke' in msg_txt:
                    self.msg_writer.write_joke(event['channel'])
                elif 'attachment' in msg_txt:
                    self.msg_writer.demo_attachment(event['channel'])
                elif 'echo' in msg_txt:
                    self.msg_writer.send_message(event['channel'], msg_txt)
                elif msg_txt is not None:
                    if 'グルメ' in msg_txt:
                        if len(prefs) == 0:
                            purp_g = True
                            self.msg_writer.write_initial(True, event['channel'])
                            continue
                    elif '思い出' in msg_txt:
                        if len(prefs) == 0:
                            purp_r = True
                            self.msg_writer.write_initial(True, event['channel'])
                            continue
                    else:
                        for cn in C_n2c:
                            if cn not in msg_txt:
                                continue
                            else:
                                nation = cn
                                prefs =  self.msg_writer.get_PrefTop2_fromNation([nation], event['channel'])
                                inp = ['c', cn]
                                break

                        for pn in P_n2c:
                            if pn not in msg_txt:
                                continue
                            else:
                                pref = pn
                                nations = get_NationTop2_fromPref(pref)
                                prefs = self.msg_writer.get_PrefTop2_fromNation(nations, event['channel'])
                                inp = ['p', pn]
                                break
                    self.suggest(inp, prefs, purp_g, purp_r)
                else:
                    self.msg_writer.write_prompt(event['channel'])
                '''
                elif countryList[countryList['countryName'].str.contains(str(msg_txt))]:
                    self.send_message(event['channel'], "検索しているので、少し待ってね :-)")
                    # 国籍から都道府県Top2のコードを取得
                        
                    in_nation = countryList[countryList['countryName'].str.contains(str(msg_txt))]['countryName']
                    pref1, pref2 = get_PrefTop2_fromNation(in_nation)
                    self.send_message(event['channel'], "あと少し待ってね :-)")
                    # 各都道府県に対して情報を取得: pref1, 2
                    #食べログ: url_tabe = URLが格納されたリスト
                    url_tabe_list = get_taberogu_url([pref1, pref2])
                    #あそびゅー
                    url_aso_list = get_asoview_url([pref1, pref2])
                    # 情報を提示
                    #
                # 都道府県を入力されたら、その都道府県が人気な国籍Top2を取得し、各国籍での人気都道府県Top2を取得し、情報を推薦する
                elif prefList[prefList['prefName'.str.contains(str(msg_txt))]]:
                    self.send_message(event['channel'], "検索しているので、少し待ってね :-)")                    
                    # 都道府県が人気な国籍Top2のコードを取得
                    pref0 = prefList[prefList['prefName'.str.contains(str(msg_txt))]]['prefCd']
                    nationCd3, nationCd4 = get_NationTop2_fromPref(pref0)
                    self.send_message(event['channel'], "もう少し待ってね :-)")
                    # 各国籍に対して人気都道府県Top2のコードを取得
                    pref3, pref4 = get_PrefTop2_fromNation(nationCd3)
                    pref5, pref6 = get_PrefTop2_fromNation(nationCd4)
                    self.send_message(event['channel'], "あと少し待ってね :-)")
                    # 各都道府県に対して情報を取得: pref0, 3, 4, 5, 6
                    #食べログ: url_tabe = URLが格納されたリスト
                    url_tabe_list = get_taberogu_url([pref0, pref3, pref4, pref5, pref6])
                    #あそびゅー
                    url_aso_list = get_asoview_url([pref0, pref3, pref4, pref5, pref6])
                    # 情報を提示
                    #
                '''

    def _is_direct_message(self, channel):
        """Check if channel is a direct message channel

        Args:
            channel (str): Channel in which a message was received
        """
        return channel.startswith('D')

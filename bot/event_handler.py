
import json
import logging
import re
import requests
import pandas as pd
from pandas import DataFrame

logger = logging.getLogger(__name__)

# 国籍と都道府県の名前とコード変換リストを読み込み
countryList = pd.read_csv("data/CountryList.csv", names = ('regionCd', 'regionName', 'countryCd', 'countryName'))
prefList = pd.read_csv("data/PrefExchangeList.csv", names = ('prefName', 'shortName', 'prefCd'))


class RtmEventHandler(object):
    def __init__(self, slack_clients, msg_writer):
        self.clients = slack_clients
        self.msg_writer = msg_writer

    def handle(self, event):

        if 'type' in event:
            self._handle_by_type(event['type'], event)

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
                # 国籍を入力されたら、その国籍に人気の都道府県Top2を取得し、情報を推薦する
                elif countryList[countryList['countryName'].str.contains(str(msg_txt))]:
                    # 国籍から都道府県Top2のコードを取得
                    in_nation = countryList[countryList['countryName'].str.contains(str(msg_txt))]['countryName']
                    pref1, pref2 = get_PrefTop2_fromNation(in_nation)
                    # 各都道府県に対して情報を取得: pref1, 2
                    print "処理を実装"
                    url1 = get_taberogu_url(pref1)
                    url2 = get_taberogu_url(pref2)
                    # 情報を提示
                # 都道府県を入力されたら、その都道府県が人気な国籍Top2を取得し、各国籍での人気都道府県Top2を取得し、情報を推薦する
                elif prefList[prefList['prefName'.str.contains(str(msg_txt))]]:
                    # 都道府県が人気な国籍Top2のコードを取得
                    in_pref = prefList[prefList['prefName'.str.contains(str(msg_txt))]]['prefCd']
                    nationCd3, nationCd4 = get_NationTop2_fromPref(in_pref)
                    # 各国籍に対して人気都道府県Top2のコードを取得
                    pref3, pref4 = get_PrefTop2_fromNation(nationCd3)
                    pref5, pref6 = get_PrefTop2_fromNation(nationCd4)
                    # 入力された都道府県コードを取得
                    pref0 = get_prefCd(in_pref)
                    # 各都道府県に対して情報を取得: pref0, 3, 4, 5, 6
                    print "処理を実装"
                    # 情報を提示
                else:
                    self.msg_writer.write_prompt(event['channel'])

    def _is_direct_message(self, channel):
        """Check if channel is a direct message channel

        Args:
            channel (str): Channel in which a message was received
        """
        return channel.startswith('D')

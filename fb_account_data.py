# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from facebook_business import FacebookSession
from facebook_business import FacebookAdsApi
from facebook_business.adobjects.campaign import Campaign as AdCampaign
from facebook_business.adobjects.adaccountuser import AdAccountUser as AdUser
from facebook_business.adobjects.adaccount import AdAccount
import json
import os
import pandas as pd
from datetime import date, timedelta
import click
import pprint

pp = pprint.PrettyPrinter(indent=4)
this_dir = os.path.dirname(__file__)
config_filename = os.path.join(this_dir, 'config.json')
with open(config_filename) as config_file:
    config = json.load(config_file)

session = FacebookSession(
   config['app_id'],
   config['app_secret'],
   config['access_token'],
)
api = FacebookAdsApi(session)
start_date = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
end_date = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')


def deal_insight(insight):
    data_dict = {}
    for stat in insight:
        for statfield in stat:
            if statfield != 'actions':
                data_dict[statfield] = stat[statfield]
            else:
                for i in stat[statfield]:
                    if i.get('action_type') == 'mobile_app_install':
                        data_dict[statfield] = i.get('value')
    return data_dict


if __name__ == '__main__':
    FacebookAdsApi.set_default_api(api)
    me = AdUser(fbid='me')
    input_data_list = []
    my_accounts_list = list(me.get_ad_accounts())
    for account in my_accounts_list:
        account_insight = account.get_insights(fields=['account_id',
                                                       'account_name',
                                                       'impressions',
                                                       'clicks',
                                                       'spend',
                                                       'ctr',
                                                       'actions'],
                                                params={'date_preset': 'yesterday'})
        data_dict = deal_insight(account_insight)
        if data_dict:
            input_data_list.append(data_dict)

    df = pd.DataFrame(input_data_list)
    df.fillna(0, inplace=True)
    df['actions'] = df['actions'].astype(int)
    df['clicks'] = df['clicks'].astype(int)
    df['impressions'] = df['impressions'].astype(int)
    df['spend'] = df['spend'].astype(float)
    df['ctr'] = df['ctr'].astype(float)
    df.to_excel('test.xlsx', index=False)


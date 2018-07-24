# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

﻿from facebook_business import FacebookSession
from facebook_business import FacebookAdsApi
from facebook_business.api import FacebookAdsApiBatch
from facebook_business.adobjects.campaign import Campaign as AdCampaign
from facebook_business.adobjects.adaccountuser import AdAccountUser as AdUser
from facebook_business.adobjects.adaccount import AdAccount
import json
import os
import pandas as pd
from datetime import date, timedelta
import click
import pprint
import time
from functools import partial

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


def generate_batches(iterable, batch_size_limit):
    """
    Generator that yields lists of length size batch_size_limit containing
    objects yielded by the iterable.
    """
    batch = []

    for item in iterable:
        if len(batch) == batch_size_limit:
            yield batch
            batch = []
        batch.append(item)

    if len(batch):
        yield batch


if __name__ == '__main__':
    start = time.time()
    FacebookAdsApi.set_default_api(api)
    me = AdUser(fbid='me')
    input_data_list = []
    my_accounts_list = list(me.get_ad_accounts())
    fields = ['account_id',
              'account_name',
              'impressions',
              'clicks',
              'spend',
              'ctr',
              'actions']
    params = {'date_preset': 'yesterday'}
    to_do_list = []


    def add_to_list(response):
        to_do_list.append(response.json())
        return to_do_list


    def print_to(response):
        print(response)


    for accounts in generate_batches(my_accounts_list, 25):
        api_batch = FacebookAdsApiBatch(api)

        for account in accounts:
            account_insight = account.get_insights(fields=fields,
                                                   params=params,
                                                   batch=api_batch)

            api_batch.add_request(account_insight, success=add_to_list, failure=print_to)
        api_batch.execute()

    for json_response in to_do_list:
        data = json_response.get('data')
        if data:
            data_dict = deal_insight(data)
            input_data_list.append(data_dict)

    df = pd.DataFrame(input_data_list)
    df.fillna(0, inplace=True)
    df['actions'] = df['actions'].astype(int)
    df['clicks'] = df['clicks'].astype(int)
    df['impressions'] = df['impressions'].astype(int)
    df['spend'] = df['spend'].astype(float)
    df['ctr'] = df['ctr'].astype(float)
    df.to_excel('test.xlsx', index=False)
    end = time.time()
    print(f"{end - start:0.2f}")


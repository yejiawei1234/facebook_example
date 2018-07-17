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




this_dir = os.path.dirname(__file__)
config_filename = os.path.join(this_dir, 'config.json')

config_file = open(config_filename)
config = json.load(config_file)
config_file.close()

### Setup session and api objects
#session = FacebookSession(
#    config['app_id'],
#    config['app_secret'],
#    config['access_token'],
#)
#api = FacebookAdsApi(session)

auth_info = (
    config['app_id'],
    config['app_secret'],
    config['access_token'])
FacebookAdsApi.init(*auth_info)
my_account = AdAccount(config['act_id'])
start_date = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
end_date = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')


def get_campaign_data(account, start_date, end_date):
    input_data_list = []
    for campaign in account.get_campaigns(fields=[AdCampaign.Field.name]):
        my_insights = campaign.get_insights(fields=[
                                                    'campaign_id',
                                                    'campaign_name',
                                                    'impressions',
                                                    'clicks',
                                                    'spend',
                                                    'actions',
                                                    'ctr'
                                                    ],
                                            params= {'time_range': {'since': start_date,
                                                                    'until': end_date},
                                                     'time_increment': 1})
        
        for stat in my_insights:
            data_dict = {}
            for statfield in stat:
#                print("\t%s:\t\t%s" % (statfield, stat[statfield]))
                if statfield != 'actions':
                    data_dict[statfield] = stat[statfield]
                    print(statfield)
                else:
                    for i in stat[statfield]:
                        if i.get('action_type') == 'mobile_app_install':
                            data_dict[statfield] = i.get('value')
            input_data_list.append(data_dict)
    return input_data_list

def deal_df(input_data_list, outputdir, filename):
    out_put_df = pd.DataFrame(input_data_list)
    columns = out_put_df.columns
    
    if 'spend' in columns:
        out_put_df['spend'] = out_put_df['spend'].astype(float)
    if 'actions' in columns:    
        out_put_df['actions'] = out_put_df['actions'].astype(float)
    if 'clicks' in columns:      
        out_put_df['clicks'] = out_put_df['clicks'].astype(int)
    if 'impressions' in columns:      
        out_put_df['impressions'] = out_put_df['impressions'].astype(int)
    if 'ctr' in columns:      
        out_put_df['ctr'] = out_put_df['ctr'].astype(float)
    out_put_df = out_put_df[['campaign_id','campaign_name','date_start','date_stop','impressions','clicks','ctr','actions','spend']]
    out_put_df.to_excel(f'{outputdir}/{filename}.xlsx', index=False)
    
    
def output_folder(output):
    if not os.path.isabs(output):
        home_path = os.path.expanduser('~/Desktop')
        output_folder_path = os.path.join(home_path, output)
        if os.path.exists(output_folder_path):
            print(output_folder_path)
            return output_folder_path
        else:
            print('the output folder is not existed, creating the folder now')
            os.mkdir(output_folder_path)
            return output_folder_path
    else:
        if os.path.exists(output):
            print('-------', output)
            return output
        else:
            print('the output folder is not existed, creating the folder now')
            os.mkdir(output)
            return output


@click.command()
@click.option('--output', '-o', default='output', help='The output folder')
@click.option('--start', '-s', default=start_date, help='The start date')
@click.option('--end', '-e', default=end_date, help='The end date')
@click.option('--filename', '-f', default='test', help='The output filename')
def main(output, start, end, filename):
    my_account = AdAccount(config['act_id'])
    output_folder_path = output_folder(output)
    df_list = get_campaign_data(my_account, start, end)
    deal_df(df_list, output_folder_path, filename)
    

if __name__ == '__main__':
    main()

#use this to convert user, voc, sms and app datasets into desired format
#######
#usage#
#######
# 1. Load the user, voc, sms and app datasets
# 2. combine = FeatureEngineer(user=test_user,sms=test_sms,voc=test_voc,app=test_app).combine()

import numpy as np
import pandas as pd

class CleanVOC:
    def __init__(self, voc_df):
        self.voc_df = voc_df
        self.call_dur = None
        self.calltype_id = None
        self.county_name = None
        self.opposite_no_m = None
        self.voc_df_cleaned = None

    def clean_call_dur_voc(self):
        call_dur = self.voc_df[['phone_no_m', 'call_dur'
                                ]].groupby('phone_no_m').mean().reset_index()
        print('done engineering call_dur')
        self.call_dur = call_dur
        return self

    def clean_calltype_id_voc(self):
        calltype_id = pd.get_dummies(self.voc_df[['phone_no_m','calltype_id']],columns=['calltype_id']).\
                    groupby('phone_no_m').mean().reset_index()
        calltype_id.columns = [
            'phone_no_m', 'voc_calltype_1', 'voc_calltype_2', 'voc_calltype_3'
        ]
        print('done engineering calltype_id')
        self.calltype_id = calltype_id
        return self

    def clean_county_name_voc(self):
        county_name = self.voc_df[['phone_no_m','county_name']].\
                groupby('phone_no_m')['county_name'].nunique().reset_index()
        county_name.columns = ['phone_no_m', 'voc_receive_unique_county']
        print('done engineering county_name')
        self.county_name = county_name
        return self

    def clean_opposite_no_m_voc(self):
        opposite_no_m = self.voc_df[['phone_no_m','opposite_no_m']].\
                groupby('phone_no_m')['opposite_no_m'].nunique().reset_index()
        opposite_no_m.columns = ['phone_no_m', 'voc_opposite_no_m']
        print('done engineering opposite_no_m')
        self.opposite_no_m = opposite_no_m
        return self

    def clean_voc(self):
        self.clean_call_dur_voc()
        self.clean_calltype_id_voc()
        self.clean_county_name_voc()
        self.clean_opposite_no_m_voc()
        train_voc = pd.merge(self.call_dur,
                             self.opposite_no_m,
                             on='phone_no_m',
                             how='outer')
        train_voc = pd.merge(train_voc,
                             self.calltype_id,
                             on='phone_no_m',
                             how='outer')
        train_voc = pd.merge(train_voc,
                             self.county_name,
                             on='phone_no_m',
                             how='outer')
        self.voc_df_cleaned = train_voc
        print('done engineering')
        return self.voc_df_cleaned

class CleanSMS:
    def __init__(self, sms_df):
        self.sms_df = sms_df
        self.opposite_no_m = None
        self.calltype_id = None
        self.sms_df_cleaned = None

    def clean_opposite_no_m_sms(self):
        opposite_no_m = (self.sms_df[['phone_no_m','opposite_no_m']].\
                groupby('phone_no_m').count()/self.sms_df[['phone_no_m','opposite_no_m']].\
                groupby('phone_no_m').nunique()).drop('phone_no_m',axis=1).reset_index()
        opposite_no_m.columns = ['phone_no_m', 'sms_per_receiver']
        self.opposite_no_m = opposite_no_m
        print('done engineering opposite_no_m')
        return self

    def clean_calltype_id_sms(self):
        calltype_id = pd.get_dummies(self.sms_df[['phone_no_m','calltype_id']],
                             columns=['calltype_id'], prefix='sms_calltype').\
                groupby('phone_no_m').mean().reset_index()
        self.calltype_id = calltype_id
        print('done engineering calltype_id')
        return self

    def clean_sms(self):
        self.clean_opposite_no_m_sms()
        self.clean_calltype_id_sms()
        sms_df = pd.merge(self.opposite_no_m,
                          self.calltype_id,
                          on='phone_no_m',
                          how='outer')
        self.sms_df_cleaned = sms_df
        print('done engineering')
        return self.sms_df_cleaned

class CleanAPP:
    def __init__(self,app_df):
        self.app_df = app_df
        self.flow = None
        self.busi_name = None
        self.app_df_cleaned = None

    def clean_flow_app(self):
        flow = self.app_df[['phone_no_m','flow']].groupby('phone_no_m').mean().reset_index()
        flow.columns = ['phone_no_m','network_usage']
        print('done engineering flow')
        self.flow = flow
        return self

    def clean_busi_name_app(self):
        busi_name = self.app_df[['phone_no_m','busi_name']]
        busi_name['busi_name'].where(busi_name['busi_name'].isna(),'yes',inplace=True)
        busi_name['busi_name'].where(~busi_name['busi_name'].isna(),'no',inplace=True)
        busi_name = pd.get_dummies(busi_name,columns=['busi_name'],prefix='data_with_known_app')
        busi_name = busi_name.groupby('phone_no_m').mean().reset_index()
        print('done engineering busi_name')
        self.busi_name = busi_name
        return self

    def clean_app(self):
        self.clean_flow_app()
        self.clean_busi_name_app()
        app_df = pd.merge(self.busi_name,self.flow,on='phone_no_m',how='outer')
        self.app_df_cleaned = app_df
        print('done engineering')
        return self.app_df_cleaned

class FeatureEngineer:
    def __init__(self, user, sms, voc, app, training=True):
        self.user = user
        self.sms = sms
        self.voc = voc
        self.app = app
        self.training = training

    def clean(self):
        sms = CleanSMS(self.sms).clean_sms()
        self.sms = sms
        voc = CleanVOC(self.voc).clean_voc()
        self.voc = voc
        app = CleanAPP(self.app).clean_app()
        self.app = app
        print('done engineering all features')
        return self
    
    def combine(self):
        self.clean()
        self.user = pd.merge(self.user, self.sms, on='phone_no_m', how='left')
        self.user = pd.merge(self.user, self.voc, on='phone_no_m', how='left')
        self.user = pd.merge(self.user, self.app, on='phone_no_m', how='left')
        print('done merging all features')
        return self.user

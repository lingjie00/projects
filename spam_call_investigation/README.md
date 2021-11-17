# Spam Call Investigation
Investigating spam calls from telecommunication data

Competition link: http://www.scdata.net.cn/common/cmpt/%E8%AF%88%E9%AA%97%E7%94%B5%E8%AF%9D%E8%AF%86%E5%88%AB_%E8%B5%9B%E9%A2%98%E4%B8%8E%E6%95%B0%E6%8D%AE.html

## Propose model:
train_user:\
spam call = county + idcard + average_mth_spending

train_voc:\
spam call = avg_call_duration + num_unique_receiver + avg_calltype_id_type + num_unique_receiver_county

train_sms:\
spam call = avg_num_SMS_sent_per_receiver + avg_calltype_id_type

train_app:\
spam call = known_app_internet_usage + unknown_app_internet_usage

### overall model:
spam call = county + idcard + average_mth_spending + avg_call_duration + num_unique_receiver + avg_calltype_id_type + num_unique_receiver_county + avg_num_SMS_sent_per_receiver + avg_calltype_id_type + known_app_internet_usage + unknown_app_internet_usage

## Feature engineering:
Clean concept applied is by averaging the user's aggregate behaviour, for example: the average SMS sent by the user

engineer_dataset.py in feature engineering contains the program to conduct feature engineering. Other files in feature engineering folder contains the detailed steps.

## Model training:
Model training folder contains the model training steps taken

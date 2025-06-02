import pandas as pd
import uuid

try:
    df_ad_events = pd.read_csv('ad_events.csv')
    df_users = pd.read_csv('users.csv')
    df_campaigns = pd.read_csv('campaigns.csv')
    print("Дані успішно завантажено.")
except FileNotFoundError as e:
    print(f"Помилка: Файл не знайдено - {e}. Переконайтеся, що CSV-файли знаходяться в тій же директорії, що й скрипт.")
    exit()

# Нормалізація таблиці Advertisers
df_advertisers = df_campaigns[['AdvertiserName']].drop_duplicates().reset_index(drop=True)
df_advertisers['AdvertiserID'] = df_advertisers.index + 1
print("\nТаблиця Advertisers:")
print(df_advertisers.head())

# Нормалізація таблиці Campaigns
df_campaigns_normalized = pd.merge(
    df_campaigns,
    df_advertisers,
    on='AdvertiserName',
    how='left'
)
df_campaigns_normalized['CampaignName'] = df_campaigns_normalized['CampaignName'].astype(str).str.strip().str.lower()

df_campaigns_final = df_campaigns_normalized[[
    'CampaignID', 'AdvertiserID', 'CampaignName', 'CampaignStartDate',
    'CampaignEndDate', 'TargetingCriteria', 'AdSlotSize', 'Budget', 'RemainingBudget'
]].copy()
print("\nТаблиця Campaigns:")
print(df_campaigns_final.head())

# Нормалізація таблиці Users
df_users_final = df_users.copy()
df_users_final['SignupDate'] = pd.to_datetime(df_users_final['SignupDate']).dt.date
print("\nТаблиця Users:")
print(df_users_final.head())

# Нормалізація таблиць Interests та UserInterests
temp_interests_dropna = df_users['Interests'].dropna()

if temp_interests_dropna.empty:
    df_interests = pd.DataFrame(columns=['InterestName', 'InterestID'])
    df_user_interests_final = pd.DataFrame(columns=['UserID', 'InterestID'])
else:
    temp_split_and_strip = temp_interests_dropna.astype(str).apply(lambda x: [i.strip().strip('"') for i in x.split(',')])
    all_interests_exploded = temp_split_and_strip.explode()
    all_interests_cleaned = all_interests_exploded[all_interests_exploded != ''].drop_duplicates()

    if all_interests_cleaned.empty:
        df_interests = pd.DataFrame(columns=['InterestName', 'InterestID'])
        df_user_interests_final = pd.DataFrame(columns=['UserID', 'InterestID'])
    else:
        df_interests = pd.DataFrame({'InterestName': all_interests_cleaned.values}).reset_index(drop=True)
        df_interests['InterestID'] = df_interests.index + 1

        df_user_interests_temp = df_users[['UserID', 'Interests']].dropna()
        df_user_interests_long = df_user_interests_temp.assign(
            Interests=df_user_interests_temp['Interests'].astype(str).str.split(',')
        ).explode('Interests')

        df_user_interests_long['Interests'] = df_user_interests_long['Interests'].str.strip().str.strip('"')
        df_user_interests_long = df_user_interests_long[df_user_interests_long['Interests'] != '']

        df_user_interests_final = pd.merge(
            df_user_interests_long,
            df_interests,
            left_on='Interests',
            right_on='InterestName',
            how='left'
        )[['UserID', 'InterestID']].drop_duplicates().reset_index(drop=True)
print("\nТаблиця Interests:")
print(df_interests.head())
print("\nТаблиця UserInterests:")
print(df_user_interests_final.head())

# Нормалізація таблиці Impressions
# EventID у df_ad_events містить Campaign_XXX
df_ad_events['CampaignName_For_Merge'] = df_ad_events['EventID'].astype(str).str.strip().str.lower()

df_impressions_temp = pd.merge(
    df_ad_events,
    df_campaigns_final[['CampaignID', 'CampaignName']],
    left_on='CampaignName_For_Merge',
    right_on='CampaignName',
    how='left'
)

df_impressions_final = df_impressions_temp[[
    'EventID', 'CampaignID', 'UserID', 'Device', 'Location',
    'Timestamp', 'BidAmount', 'AdCost'
]].copy()

df_impressions_final = df_impressions_final.rename(columns={'EventID': 'ImpressionID'})
df_impressions_final['Timestamp'] = pd.to_datetime(df_impressions_final['Timestamp'])
print("\nТаблиця Impressions:")
print(df_impressions_final.head())


# Нормалізація таблиці Clicks
df_clicks_raw = df_ad_events[df_ad_events['WasClicked'] == True].reset_index(drop=True).copy()
df_clicks_final = df_clicks_raw[[
    'EventID', 'ClickTimestamp', 'AdRevenue'
]].copy()

df_clicks_final['ClickID'] = df_clicks_final.index + 1
df_clicks_final = df_clicks_final.rename(columns={'EventID': 'ImpressionID'})
df_clicks_final['ClickTimestamp'] = pd.to_datetime(df_clicks_final['ClickTimestamp'])
print("\nТаблиця Clicks:")
print(df_clicks_final.head())

# Збереження трансформованих даних у CSV-файли
df_advertisers.to_csv('advertisers.csv', index=False)
df_campaigns_final.to_csv('campaigns_normalized.csv', index=False)
df_users_final.to_csv('users_normalized.csv', index=False)
df_interests.to_csv('interests.csv', index=False)
df_user_interests_final.to_csv('user_interests.csv', index=False)
df_impressions_final.to_csv('impressions.csv', index=False)
df_clicks_final.to_csv('clicks.csv', index=False)

print("\nТрансформація даних завершена. Дані збережено у відповідні CSV-файли.")

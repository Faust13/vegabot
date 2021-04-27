import os

#general
clan_name = os.environ.get("CLAN_NAME", "VEGA")
platform = os.environ.get("PLATFORM", "Xbox")

#Airtable Connection
atb_api_key = os.environ.get("ATB_API_KEY")
atb_base_key = os.environ.get("ATB_BASE_KEY")
atb_table = os.environ.get("ATB_TABLE")
#Telegram settings
tg_api_key = os.environ.get("TG_API_KEY")
admin_chat = os.environ.get("TG_ADMN_CHAT_ID", "-123") #ID чата администрации клана, куда будут поступать заявки на вступление
#Destiny 2 API
d2_api_root = os.environ.get("D2_API_ROOT", "https://www.bungie.net/Platform")
d2_app_api_key = os.environ.get("D2_APP_API_KEY", '4673fbf037a64680b0dfb1d369f7c035')

#Links
clan_chat_link = os.environ.get("CHAT_CLAN_LINK", "https://t.me/GuardianFM")
lfg_chat_link = os.environ.get("LFG_CLAN_LINK", "https://t.me/GuardianFM")
bnet_clan_link = os.environ.get("BNET_CLAN_LINK", "https://www.bungie.net/ru/ClanV2?groupid=2135560")


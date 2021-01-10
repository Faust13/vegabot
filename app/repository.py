import airtable

atb_api_key = ''
atb_base_key = ''
atb_table = ''


class UserRepository:
    airtable = airtable.Airtable(atb_base_key, atb_table, atb_api_key)

    def add_user(self, telegram_tag: str, chat_id: str):
        data = self.airtable.search('tg', telegram_tag)
        if not data:
            self.airtable.insert({'tg': telegram_tag, 'chat_id': chat_id})

    def get_user(self, telegram_tag: str) -> dict:
        data = self.airtable.search('tg', telegram_tag)
        if data:
            return data[0]

    def change_user(self, telegram_tag: str, property_name: str, property_value):
        self.airtable.update_by_field('tg', telegram_tag, {property_name: property_value})

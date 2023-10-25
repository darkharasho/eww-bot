import pdb

from peewee import *
from playhouse.sqlite_ext import *
from src import settings
from src.bot_client import bot
from src.models.base_model import BaseModel


class Config(BaseModel):
    name = CharField(unique=True)
    guild_id = IntegerField()
    value = JSONField()
    value_type = TextField()

    @classmethod
    def guild_member_role_id(cls):
        value = cls.select().where(cls.name == "guild_member_role_id").first()
        if value:
            return value.get_value()
        else:
            raise "guild_member_role_id not found"

    @classmethod
    def disabled_modules(cls):
        value = cls.select().where(cls.name == "disabled_modules").first()
        if value:
            return value.get_value()
        else:
            return []

    @classmethod
    def allowed_admin_role_ids(cls):
        value = cls.select().where(cls.name == "allowed_admin_role_ids").first()
        if value:
            return value.get_value()
        else:
            return []

    @classmethod
    def build_manager_role_ids(cls):
        value = cls.select().where(cls.name == "build_manager_role_ids").first()
        if value:
            return value.get_value()
        else:
            return []

    @classmethod
    def commander_role_ids(cls):
        value = cls.select().where(cls.name == "commander_role_ids").first()
        if value:
            return value.get_value()
        else:
            return []

    @classmethod
    def raid_days(cls):
        value = cls.select().where(cls.name == "raid_days").first()
        if value:
            return value.get_value()
        else:
            return []

    @classmethod
    def review_forum_channel_id(cls):
        value = cls.select().where(cls.name == "review_forum_channel_id").first()
        if value:
            return value.get_value()
        else:
            return None

    @classmethod
    def build_forum_channel_id(cls):
        value = cls.select().where(cls.name == "build_forum_channel_id").first()
        if value:
            return value.get_value()
        else:
            raise "No Build Forum Channel set."

    @classmethod
    def build_update_channel_id(cls):
        value = cls.select().where(cls.name == "build_update_channel_id").first()
        if value:
            return value.get_value()
        else:
            raise "No Build Update Channel set."

    @classmethod
    def bot_chat_channel_ids(cls):
        value = cls.select().where(cls.name == "bot_chat_channel_ids").first()
        if value:
            return value.get_value()
        else:
            return []

    @classmethod
    def auto_attendance(cls, nested_cfg=None):
        if not nested_cfg:
            nested_cfg = []
        value = cls.select().where(cls.name == "auto_attendance").first()
        if value:
            if nested_cfg:
                current_dict = value.get_value()

                # Traverse the dictionary using the keys
                for key in nested_cfg:
                    if key in current_dict:
                        current_dict = current_dict[key]
                    else:
                        # Handle the case where a key is not found
                        print(f"Key '{key}' not found.")
                        break
                if current_dict in ["True", "true", "False", "false"]:
                    return eval(current_dict.title())
                return current_dict
            else:
                return value.get_value()
        else:
            return {}

    @classmethod
    def raid_notification(cls, nested_cfg=None):
        if not nested_cfg:
            nested_cfg = []
        value = cls.select().where(cls.name == "raid_notification").first()
        if value:
            if nested_cfg:
                current_dict = value.get_value()

                # Traverse the dictionary using the keys
                for key in nested_cfg:
                    if key in current_dict:
                        current_dict = current_dict[key]
                    else:
                        # Handle the case where a key is not found
                        print(f"Key '{key}' not found.")
                        break
                    if current_dict in ["True", "true", "False", "false"]:
                        return eval(current_dict.title())
                return current_dict
            else:
                return value.get_value()
        else:
            return {}

    @classmethod
    def raid_reminder(cls, nested_cfg=None):
        if not nested_cfg:
            nested_cfg = []
        value = cls.select().where(cls.name == "raid_reminder").first()
        if value:
            if nested_cfg:
                current_dict = value.get_value()

                # Traverse the dictionary using the keys
                for key in nested_cfg:
                    if key in current_dict:
                        current_dict = current_dict[key]
                    else:
                        # Handle the case where a key is not found
                        print(f"Key '{key}' not found.")
                        break
                if current_dict in ["True", "true", "False", "false"]:
                    return eval(current_dict.title())
                else:
                    return current_dict
            else:
                return value.get_value()
        else:
            return {}

    @classmethod
    def arcdps_updates(cls, nested_cfg=None):
        if not nested_cfg:
            nested_cfg = []
        value = cls.select().where(cls.name == "arcdps_updates").first()
        if value:
            if nested_cfg:
                current_dict = value.get_value()

                # Traverse the dictionary using the keys
                for key in nested_cfg:
                    if key in current_dict:
                        current_dict = current_dict[key]
                    else:
                        # Handle the case where a key is not found
                        print(f"Key '{key}' not found.")
                        break
                if current_dict in ["True", "true", "False", "false"]:
                    return eval(current_dict.title())
                else:
                    return current_dict
            else:
                return value.get_value()
        else:
            return {}

    @classmethod
    def game_updates(cls, nested_cfg=None):
        if not nested_cfg:
            nested_cfg = []
        value = cls.select().where(cls.name == "game_updates").first()
        if value:
            if nested_cfg:
                current_dict = value.get_value()

                # Traverse the dictionary using the keys
                for key in nested_cfg:
                    if key in current_dict:
                        current_dict = current_dict[key]
                    else:
                        # Handle the case where a key is not found
                        print(f"Key '{key}' not found.")
                        break
                if current_dict in ["True", "true", "False", "false"]:
                    return eval(current_dict.title())
                else:
                    return current_dict
            else:
                return value.get_value()
        else:
            return {}

    @classmethod
    def create_or_update(cls, name=str, value=None):
        config = cls.select().where(cls.name == name).first()
        value_type = type(value).__name__
        try:
            if config:
                (Config.update(value=value, value_type=value_type)
                 .where(Config.id == config.id)
                 .execute())
                action = "update"
                config = cls.select().where(cls.id == config.id).first()
            else:
                action = "create"
                config = cls.create(name=name,
                                    value=value,
                                    value_type=value_type,
                                    guild_id=settings.GUILD_ID)
            return config, action
        except Exception as e:
            print(f"[ERR] {e}")
            return False, "Failed"

    # Ensure that we are correctly casting the value
    def get_value(self):
        if self.value_type == "str":
            return str(self.value)
        elif self.value_type == "int":
            return int(self.value)
        else:
            return self.value

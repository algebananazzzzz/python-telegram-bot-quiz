from telegram.ext import BasePersistence, PersistenceInput
from copy import deepcopy
import json
from redis.exceptions import ResponseError
from collections import defaultdict
from typing import Any, DefaultDict, Dict, Optional, Tuple, Union
from telegram.ext._utils.types import BD, CD, UD, CDCData, ConversationDict, ConversationKey


class MyPersistence(BasePersistence[UD, CD, BD]):
    '''Using Redis to make the bot persistent'''

    def __init__(self, redis_conn, redis_key: str, active_users: list = list(), active_chats: list = list(), store_data: Optional[PersistenceInput] = None, update_interval: float = 60):
        super().__init__(store_data=store_data, update_interval=update_interval)
        self.redis_conn = redis_conn
        self.redis_key: str = redis_key
        self.user_data: Optional[Dict[int, UD]] = None
        self.chat_data: Optional[Dict[int, CD]] = None
        self.bot_data: Optional[BD] = None
        self.callback_data: Optional[CDCData] = None
        self.conversations: Optional[Dict[str,
                                          Dict[Tuple[Union[int, str], ...], object]]] = None
        self.active_users = active_users
        self.active_chats = active_chats

    def load_bot_data(self):
        """
        Load bot data from Redis and update the internal bot_data dictionary.
        """
        if not self.bot_data:
            try:
                bot_data = self.redis_conn.hget(self.redis_key, "bot_data")
                bot_data = json.loads(bot_data) if bot_data else {}
            except ResponseError as e:
                bot_data = dict()
                print(e)
                pass

            self.bot_data = bot_data
            return bot_data
        return self.bot_data

    def load_user_data(self):
        """
        Load user data from Redis and update the internal user_data dictionary.

        This function is designed to be invoked whenever there is a change in the self.active_users list. 
        In such cases, it becomes necessary to fetch updated data from the Redis server to keep the `user_data` dictionary up-to-date.
        """
        user_data = deepcopy(self.user_data) if self.user_data else {}

        user_data_pipeline = self.redis_conn.pipeline()
        loaded_users = list()

        for user_id in self.active_users:
            # Check if user_id not in self.user_data (data not already loaded)
            if user_id not in user_data.keys():
                loaded_users.append(user_id)
                user_data_pipeline.hget(self.redis_key, f"user:{user_id}")

        try:
            user_data_results = user_data_pipeline.execute()

            # Update self.user_data with the retrieved data
            user_data.update({user_id: json.loads(data) if data else {}
                              for user_id, data in zip(loaded_users, user_data_results)})

        except ResponseError as e:
            print(e)
            pass

        self.user_data = user_data
        return user_data

    def load_chat_and_conv_data(self):
        """
        Load chat and conversation data from Redis and update internal dictionaries.

        This function is designed to be invoked whenever there is a change to the `self.active_chats` list. 
        In such cases, it becomes necessary to fetch updated data from the Redis server to keep the `chat_data` and `conversations` dictionaries up-to-date.
        """
        chat_data = deepcopy(self.chat_data) if self.chat_data else {}
        conversations = deepcopy(
            self.conversations) if self.conversations else {}

        loaded_chats = list()

        chat_pipeline = self.redis_conn.pipeline()
        for chat_id in self.active_chats:
            if chat_id not in chat_data.keys():
                loaded_chats.append(chat_id)
                chat_data_key = f"chat:{chat_id}"
                chat_pipeline.hget(self.redis_key, chat_data_key)

        try:

            chat_data_redis_results = chat_pipeline.execute()
            chat_data_results = {id: json.loads(chat_data_result) if chat_data_result else {
            } for id, chat_data_result in zip(loaded_chats, chat_data_redis_results)}

            for chat_id, data in chat_data_results.items():
                chat_data[chat_id] = data.get("chat_data", {})

                conversations_data = data.get("conversations", {})

                for conv_name, conv_values in conversations_data.items():
                    for value, conv_ids in conv_values.items():
                        if conv_name in conversations:
                            conversations[conv_name][tuple(conv_ids)] = int(
                                value) if value != 'null' else None
                        else:
                            conversations[conv_name] = {tuple(conv_ids): int(
                                value) if value != 'null' else None}
        except ResponseError as e:
            print(e)
            pass

        self.chat_data = chat_data
        self.conversations = conversations

        return {'chat_data': chat_data, 'conversations': conversations}

    def load_redis(self):
        try:
            self.load_bot_data()
            self.load_user_data()
            self.load_chat_and_conv_data()

            self.callback_data = None

        except Exception as e:
            print(e)
            self.conversations = {}
            self.user_data = {}
            self.chat_data = {}
            self.bot_data = {}
            self.callback_data = None

    def dump_redis(self):
        data = {
            "bot_data": json.dumps(self.bot_data)
        }

        for key, value in self.user_data.items():
            data[f"user:{key}"] = json.dumps(value)

        chat_data = {}

        for key, value in self.chat_data.items():
            transformed_dict = {
                f"chat:{key}": {
                    'chat_data': value,
                    'conversations': {}
                }
            }
            chat_data.update(transformed_dict)

        for conv_name, conv_dict in self.conversations.items():
            for chat_id, conv_val in conv_dict.items():
                chat_key = f"chat:{chat_id[0]}"
                if chat_key in chat_data:
                    chat_data[chat_key]['conversations'][conv_name] = {
                        conv_val: chat_id}
                else:
                    chat_data[chat_key] = {'conversations': {
                        conv_name: {conv_val: chat_id}}}

        for chat_id, chat_data in chat_data.items():
            data[chat_id] = json.dumps(chat_data)

        try:
            self.redis_conn.hmset(self.redis_key, data)
        except ResponseError as e:
            print(e)
            self.redis_conn.delete(self.redis_key)
            self.redis_conn.hmset(self.redis_key, data)

    async def load_active_user(self, user_id):
        self.active_users.append(user_id)
        self.load_user_data()
        return True

    async def load_active_chat(self, chat_id):
        self.active_chats.append(chat_id)
        self.load_chat_and_conv_data()
        return True

    async def get_user_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        '''Returns the user_data from the pickle on Redis if it exists or an empty :obj:`defaultdict`.'''
        if self.user_data:
            user_data = self.user_data
        else:
            user_data = self.load_user_data()
        return deepcopy(user_data)  # type: ignore[arg-type]

    async def get_chat_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        '''Returns the chat_data from the pickle on Redis if it exists or an empty :obj:`defaultdict`.'''
        if self.chat_data:
            chat_data = self.chat_data
        else:
            chat_data = self.load_chat_and_conv_data()['chat_data']
        return deepcopy(chat_data)  # type: ignore[arg-type]

    async def get_bot_data(self) -> Dict[Any, Any]:
        '''Returns the bot_data from the pickle on Redis if it exists or an empty :obj:`dict`.'''
        if self.bot_data:
            bot_data = self.bot_data
        else:
            bot_data = self.load_bot_data()
        return deepcopy(bot_data)  # type: ignore[arg-type]

    async def get_conversations(self, name: str) -> ConversationDict:
        '''Returns the conversations from the pickle on Redis if it exsists or an empty dict.'''
        if self.conversations:
            conversations = self.conversations
        else:
            conversations = self.load_chat_and_conv_data()['conversations']
        # type: ignore[union-attr]
        return conversations.get(name, dict()).copy()

    async def get_callback_data(self):
        if self.callback_data:
            pass
        else:
            self.load_redis()
        return deepcopy(self.callback_data)

    async def update_conversation(self, name: str, key: Tuple[int, ...], new_state: Optional[object]) -> None:
        '''Will update the conversations for the given handler and depending on :attr:`on_flush` save the pickle on Redis.'''
        if not self.conversations:
            self.conversations = dict()
        if self.conversations.setdefault(name, dict()).get(key) == new_state:
            return
        self.conversations[name][key] = new_state

    async def update_user_data(self, user_id: int, data: Dict) -> None:
        '''Will update the user_data and depending on :attr:`on_flush` save the pickle on Redis.'''
        if self.user_data is None:
            self.user_data = defaultdict(dict)

        if self.user_data.get(user_id) == data:
            return
        self.user_data[user_id] = data

    async def update_chat_data(self, chat_id: int, data: Dict) -> None:
        '''Will update the chat_data and depending on :attr:`on_flush` save the pickle on Redis.'''
        if self.chat_data is None:
            self.chat_data = defaultdict(dict)

        if self.chat_data.get(chat_id) == data:
            return
        self.chat_data[chat_id] = data

    async def update_bot_data(self, data: Dict) -> None:
        '''Will update the bot_data and depending on :attr:`on_flush` save the pickle on Redis.'''
        if self.bot_data == data:
            return
        self.bot_data = data.copy()

    async def update_callback_data(self, data):
        if self.callback_data == data:
            return
        self.callback_data = data

    async def flush(self) -> None:
        '''Will save all data in memory to Redis.'''
        self.dump_redis()

    async def drop_chat_data(self, chat_id):
        if self.chat_data is None:
            return
        self.chat_data.pop(chat_id, None)

    async def drop_user_data(self, user_id):
        if self.user_data is None:
            return
        self.user_data.pop(user_id, None)

    async def refresh_user_data(self, user_id: int, user_data: Dict[Any, Any]) -> None:
        """Does nothing.

        .. versionadded:: 13.6
        .. seealso:: :meth:`telegram.ext.BasePersistence.refresh_user_data`
        """

    async def refresh_chat_data(self, chat_id: int, chat_data: Dict[Any, Any]) -> None:
        """Does nothing.

        .. versionadded:: 13.6
        .. seealso:: :meth:`telegram.ext.BasePersistence.refresh_chat_data`
        """

    async def refresh_bot_data(self, bot_data: Dict[Any, Any]) -> None:
        """Does nothing.

        .. versionadded:: 13.6
        .. seealso:: :meth:`telegram.ext.BasePersistence.refresh_bot_data`
        """

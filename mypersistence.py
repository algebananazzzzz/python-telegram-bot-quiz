from telegram.ext._utils.types import ConversationDict
from telegram.ext import BasePersistence, PersistenceInput
from copy import deepcopy
import os
from dotenv import load_dotenv
import pickle
import redis
from collections import defaultdict
from typing import Any, DefaultDict, Dict, Optional, Tuple

load_dotenv()

redis_endpoint = os.environ["REDIS_HOST"]
redis_port = os.environ["REDIS_PORT"]
redis_key = os.environ["REDIS_KEY"]

try:
    redis_conn = redis.StrictRedis(host=redis_endpoint, port=redis_port)
except Exception:
    redis_conn = None


class MyPersistence(BasePersistence):
    '''Using Redis to make the bot persistent'''

    def __init__(self, redis_key, store_data: PersistenceInput, update_interval: int):
        # super().__init__(store_user_data=True, store_chat_data=True, store_bot_data=True)
        self.store_data: PersistenceInput = store_data
        self._update_interval = update_interval
        self.redis_key = redis_key
        self.user_data: Optional[DefaultDict[int, Dict]] = None
        self.chat_data: Optional[DefaultDict[int, Dict]] = None
        self.bot_data: Optional[Dict] = None
        self.bot_data: Optional[Dict] = None
        self.conversations: Optional[Dict[str, Dict[Tuple, Any]]] = None

    def load_redis(self):
        try:
            response = redis_conn.get(redis_key)
            if response:
                response = pickle.loads(response)
                self.user_data = defaultdict(dict, response['user_data'])
                self.chat_data = defaultdict(dict, response['chat_data'])
                # For backwards compatibility with files not containing bot data
                self.bot_data = response.get('bot_data', dict())
                self.conversations = response.get('conversations', dict())
            else:
                self.conversations = dict()
                self.user_data = defaultdict(dict)
                self.chat_data = defaultdict(dict)
                self.bot_data = dict()
        except Exception as exc:
            raise exc
            self.conversations = dict()
            self.user_data = defaultdict(dict)
            self.chat_data = defaultdict(dict)
            self.bot_data = dict()

    def dump_redis(self):
        data = {
            'conversations': self.conversations,
            'user_data': self.user_data,
            'chat_data': self.chat_data,
            'bot_data': self.bot_data,
        }
        data = pickle.dumps(data)
        try:
            redis_conn.set(redis_key, data)
        except Exception as exc:
            raise exc

    async def get_user_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        '''Returns the user_data from the pickle on Redis if it exists or an empty :obj:`defaultdict`.'''
        if self.user_data:
            pass
        else:
            self.load_redis()
        return deepcopy(self.user_data)  # type: ignore[arg-type]

    async def get_chat_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        '''Returns the chat_data from the pickle on Redis if it exists or an empty :obj:`defaultdict`.'''
        if self.chat_data:
            pass
        else:
            self.load_redis()
        return deepcopy(self.chat_data)  # type: ignore[arg-type]

    async def get_bot_data(self) -> Dict[Any, Any]:
        '''Returns the bot_data from the pickle on Redis if it exists or an empty :obj:`dict`.'''
        if self.bot_data:
            pass
        else:
            self.load_redis()
        return deepcopy(self.bot_data)  # type: ignore[arg-type]

    async def get_conversations(self, name: str) -> ConversationDict:
        '''Returns the conversations from the pickle on Redis if it exsists or an empty dict.'''
        if self.conversations:
            pass
        else:
            self.load_redis()
        # type: ignore[union-attr]
        return self.conversations.get(name, dict()).copy()

    async def get_callback_data(self):
        pass

    async def update_conversation(self, name: str, key: Tuple[int, ...], new_state: Optional[object]) -> None:
        '''Will update the conversations for the given handler and depending on :attr:`on_flush` save the pickle on Redis.'''
        if not self.conversations:
            self.conversations = dict()
        if self.conversations.setdefault(name, dict()).get(key) == new_state:
            return
        self.conversations[name][key] = new_state

    async def update_user_data(self, user_id: int, data: Dict) -> None:
        '''Will update the user_data and depending on :attr:`on_flush` save the pickle on Redis.'''
        if self.store_data.user_data:
            if self.user_data is None:
                self.user_data = defaultdict(dict)
            if self.user_data.get(user_id) == data:
                return
            self.user_data[user_id] = data
        else:
            self.user_data = defaultdict(dict)

    async def update_chat_data(self, chat_id: int, data: Dict) -> None:
        '''Will update the chat_data and depending on :attr:`on_flush` save the pickle on Redis.'''
        if self.store_data.chat_data:
            if self.chat_data is None:
                self.chat_data = defaultdict(dict)
            if self.chat_data.get(chat_id) == data:
                return
            self.chat_data[chat_id] = data
        else:
            self.chat_data = defaultdict(dict)

    async def update_bot_data(self, data: Dict) -> None:
        '''Will update the bot_data and depending on :attr:`on_flush` save the pickle on Redis.'''
        if self.bot_data == data:
            return
        self.bot_data = data.copy()

    async def update_callback_data(self, data):
        pass

    async def flush(self) -> None:
        '''Will save all data in memory to pickle on Redis.'''
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

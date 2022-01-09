from binance import AsyncClient
import asyncio, os
from dotenv import load_dotenv
load_dotenv()
_MY_API = os.getenv('MY_API')
_MY_SECRECT = os.getenv('MY_SECRECT')
assert(_MY_SECRECT and _MY_API), "Binance keys are missing!"

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        # https://stackoverflow.com/a/46750562
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()
RUC = get_or_create_eventloop().run_until_complete


class _BaseAsyncClient:
    """ This class get an instance of the Async Client with keys! """
    async def _createClient(self) -> AsyncClient:
        return await AsyncClient.create(api_key=_MY_API, api_secret=_MY_SECRECT)

    def __init__(self):
        self._client = RUC(self._createClient())
        print(f'Async Client Acquired')

    def __del__(self):
        RUC(self._client.close_connection())

    @property
    def client(self):
        return self._client
_BaseClient = _BaseAsyncClient()

# This should be used everywhere!
MY_ASYNC_CLIENT = _BaseClient.client
import requests

from chat_demo.api.data import Langs
from chat_demo.logger import logger


def prepare_key_map():
    # curl -X GET "https://vertimas.vu.lt/ws/service.svc/json/GetSystemList?appID=myappid" -H "client-id: " | jq .
    return {"lt-en": "smt-8abc06a7-09dc-405c-bd29-580edc74eb05",
            "en-lt": "smt-ecbadf49-1c17-470f-a6d9-b06a54b4e46f",
            "lt-pl": "smt-ed8e89ff-982a-4214-ad79-a1e03be0c738",
            "pl-lt": "smt-6c8db4f4-18fc-4cac-8fba-ce47bc2de495",
            "lt-ru": "smt-5867533f-6573-4672-b742-28b6ac9afda0",
            "ru-lt": "smt-51dfc27c-77ef-4edd-b76d-0df6163759c6",
            "lt-de": "smt-ec6db1bc-ba3a-4f17-86c2-920b91ecd33c",
            "de-lt": "smt-a0bbff36-3641-4790-ab31-85ee2a66be71",
            "lt-fr": "smt-27d0ecdd-d79a-4870-aa18-c768cea1de96",
            "fr-lt": "smt-eb96b6b8-3d6b-4065-9f05-cb3b3d6fccb5"
            }


class Translator:

    def __init__(self, key: str, app: str):
        logger.info("Init translator")
        self.__url = f"https://vertimas.vu.lt/ws/service.svc/json/Translate?appID={app}"
        self.__key = key
        self.__key_map = prepare_key_map()

    def convert(self, txt: str, _from: Langs, _to: Langs) -> str:
        logger.info(f"Translating from {_from.to_str()} to {_to.to_str()}")
        sid = self.get_system_id(f"{_from.to_str()}-{_to.to_str()}")
        if sid == "":
            raise Exception(f"Can't find system id for {_from.to_str()}-{_to.to_str()}")
        logger.debug(f"got sid {sid}")
        in_data = {'systemID': sid, "text": txt}
        x = requests.post(self.__url, json=in_data, headers={"client-id": self.__key}, timeout=20)
        if x.status_code != 200:
            raise Exception(f"Can't translate: ({x.status_code}) {x.text}")
        data = x.json()
        logger.debug(f"got {data}")
        return data

    def get_system_id(self, param):
        logger.info(f"Getting system id for {param}")
        return self.__key_map.get(param, "")

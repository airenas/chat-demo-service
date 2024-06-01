from chat_demo.api.data import Sender, DataType, Langs


def test_sender_to_str():
    assert Sender.BOT.to_str() == "BOT"
    assert Sender.USER.to_str() == "USER"


def test_type_to_str():
    assert DataType.TEXT.to_str() == "TEXT"
    assert DataType.STATUS.to_str() == "STATUS"
    assert DataType.EVENT.to_str() == "EVENT"
    assert DataType.TEXT_RESULT.to_str() == "TEXT_RESULT"
    assert DataType.AUDIO.to_str() == "AUDIO"


def test_lang_to_str():
    assert Langs.LT.to_str() == "lt"
    assert Langs.EN.to_str() == "en"
    assert Langs.DE.to_str() == "de"
    assert Langs.PL.to_str() == "pl"
    assert Langs.FR.to_str() == "fr"


def test_lang_from_str():
    assert Langs.from_str("lt") == Langs.LT
    assert Langs.from_str("en") == Langs.EN
    assert Langs.from_str("es") == Langs.UN

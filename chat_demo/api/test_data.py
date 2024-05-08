from chat_demo.api.data import Sender, DataType


def test_sender_to_str():
    assert Sender.BOT.to_str() == "BOT"
    assert Sender.USER.to_str() == "USER"


def test_type_to_str():
    assert DataType.TEXT.to_str() == "TEXT"
    assert DataType.STATUS.to_str() == "STATUS"
    assert DataType.EVENT.to_str() == "EVENT"
    assert DataType.TEXT_RESULT.to_str() == "TEXT_RESULT"
    assert DataType.AUDIO.to_str() == "AUDIO"

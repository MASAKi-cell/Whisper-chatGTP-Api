import json
import requests
from config import voicevox_path

# 例外処理
from utils.exceptions import ExceptionsError, HttpCode

# 音声出力
from time import sleep
import pyaudio
import wave
import io

one = 1


# 音声合成処理
def post_audio(text: str) -> str | None:
    try:
        param: dict = {"text": text, "speaker": one}
        res = requests.post(f"{voicevox_path}/audio_query", params=param)
        res.raise_for_status()  # HTTPステータスコードのチェック

        return res.json()

    except requests.exceptions.HTTPError as http_err:
        raise ExceptionsError(
            status_code=http_err.response.status_code, message=str(http_err)
        )
    except requests.exceptions.ConnectionError as conn_err:
        raise ExceptionsError(
            status_code=HttpCode.INTERNAL_SERVER_ERROR, message=str(conn_err)
        )
    except Exception as e:
        print(f"An error occurred: {e}")  # その他のエラー
    return None


# 音声をバイトデータに変換
def post_synthesis(audio_query_res: str) -> bytes | None:
    try:
        params = {"speaker": one}
        headers = {"content-type": "application/json"}
        audio_query_res_json = json.dumps(audio_query_res)
        res = requests.post(
            f"{voicevox_path}/synthesis",
            data=audio_query_res_json,
            params=params,
            headers=headers,
        )
        res.raise_for_status()  # HTTPステータスコードのチェック

        return res.content
    except requests.exceptions.HTTPError as http_err:
        raise ExceptionsError(
            status_code=http_err.response.status_code, message=str(http_err)
        )
    except requests.exceptions.ConnectionError as conn_err:
        raise ExceptionsError(
            status_code=HttpCode.INTERNAL_SERVER_ERROR, message=str(conn_err)
        )
    except Exception as e:
        print(f"An error occurred: {e}")  # その他のエラー
    return None


# 音声出力
def play_wav(wav_file: bytes | None) -> None:
    FORMAT = pyaudio.paInt16  # 量子ビット
    CHANNELS = 1  # ch数
    RATE = 23000  # サンプリング周波数
    CHUNK = 2**10  # バッファサイズ
    if wav_file is not None:
        wr: wave.Wave_read = wave.open(io.BytesIO(wav_file))
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
    )

    data = wr.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wr.readframes(CHUNK)
    sleep(0.5)
    stream.close()
    p.terminate()


def text_to_voice(text: str):
    res = post_audio(text)
    if res is not None:
        synthesis = post_synthesis(res)
        play_wav(synthesis)

import json


def health(event, context):
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response

def v1_description(event, context):
    body = {
        "message": "TTS api version 1."
    }

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response

def v2_description(event, context):
    body = {
        "message": "TTS api version 2."
    }

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response

def v1_tts_description(event, context):
    body = {
        "phrase": "converta esse texto para áudio"
    }

    response = {"statusCode": 200, "body": json.dumps(body)}
    return response

def v2_tts_description(event, context):
    body =   {
    "received_phrase": "converta esse texto para áudio",
    "url_to_audio": "https://meu-buckect/audio-xyz.mp3",
    "created_audio": "02-02-2023 17:00:00"
  }
    response = {"statusCode": 200, "body": json.dumps(body)}
    return response
import boto3
import base64
import json
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

polly = boto3.client('polly')
s3 = boto3.client('s3')
now = datetime.now()

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
    try:
        # Extraindo a frase do event body
        dados = json.loads(event['body'])
        phrase = dados["phrase"]

        # Usando o Amazon Polly para converter o texto em audio
        response = polly.synthesize_speech(
            Text=phrase,
            OutputFormat='mp3',
            VoiceId='Camila',
            Engine='neural'
        )
        
        file = response['AudioStream']
        id_unico = str(uuid.uuid4())
        nome = f"{id_unico}.mp3" 

        #acl='public-read'

        #Adicionado o ficheiro no bucket
        s3.upload_fileobj(file,"my-bucket-for-audios",nome,ExtraArgs={'ACL': 'bucket-owner-full-control'})
        
        # Gerando a URL do audio
        audio_url = "https://my-bucket-for-audios.s3.amazonaws.com/"+nome  

        # formatando a data de criação
        created_audio = now.strftime("%d-%m-%Y %H:%M:%S")

        # Preparando o retorno
        body = {
            "received_phrase": phrase,
            "url_to_audio": audio_url,
            "created_audio": created_audio
        }

        return {"statusCode": 200,"body": json.dumps({"body": body})}
    
    except (ClientError, json.JSONDecodeError) as error:
        # Lidando com possiveis erros
        error_message = f"An error occurred: {str(error)}"
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }

def v2_tts_description(event, context):
    
    body =   {
        "received_phrase": "converta esse texto para áudio",
        "url_to_audio": "https://meu-buckect/audio-xyz.mp3",
        "created_audio": "02-02-2023 17:00:00"
    }
     
    response = {"statusCode": 200, "body": json.dumps(body)}
    return response
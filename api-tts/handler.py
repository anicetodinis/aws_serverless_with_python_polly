import boto3
import json
import hashlib
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
import os

polly = boto3.client('polly')
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('TABLE_NAME'))
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

        # Adicionando o ficheiro no novo bucket
        s3.upload_fileobj(file, os.getenv('BUCKET_NAME'), nome, ExtraArgs={'ACL': 'bucket-owner-full-control'})
        
        # Gerando a URL do audio
        audio_url = "https://"+os.getenv('BUCKET_NAME')+".s3.amazonaws.com/"+nome  

        # formatando a data de criação
        created_audio = now.strftime("%d-%m-%Y %H:%M:%S")

        # Preparando o retorno
        body = {
            "received_phrase": phrase,
            "url_to_audio": audio_url,
            "created_audio": created_audio
        }

        return {"statusCode": 200, "body": json.dumps({"body": body})}
    
    except (ClientError, json.JSONDecodeError) as error:
        # Lidando com possiveis erros
        error_message = f"An error occurred: {str(error)}"
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }

def v2_tts_description(event, context):
    try:
        # Extraindo a frase do event body
        dados = json.loads(event['body'])
        phrase = dados["phrase"]

        # Gerando um ID único para a transcrição de áudio
        unique_id = str(uuid.uuid4())

        # Usando o Amazon Polly para converter o texto em áudio
        response = polly.synthesize_speech(
            Text=phrase,
            OutputFormat='mp3',
            VoiceId='Camila',
            Engine='neural'
        )
        
        file = response['AudioStream']
        nome = f"{unique_id}.mp3" 

        # Adicionando o arquivo de áudio no novo bucket
        s3.upload_fileobj(file, os.getenv('BUCKET_NAME'), nome, ExtraArgs={'ACL': 'bucket-owner-full-control'})
        
        # Gerando a URL do áudio
        audio_url = f"https://{os.getenv('BUCKET_NAME')}.s3.amazonaws.com/{nome}"  

        # formatando a data de criação
        created_audio = now.strftime("%d-%m-%Y %H:%M:%S")

        # Salvando uma referência no DynamoDB
        table.put_item(
            Item={
                'Id': unique_id,
                'Phrase': phrase,
                'AudioUrl': audio_url,
                'CreatedAt': created_audio
            }
        )
        # Preparando o retorno
        body = {
            "received_phrase": phrase,
            "url_to_audio": audio_url,
            "created_audio": created_audio,
            "unique_id": unique_id
        }

        return {"statusCode": 200, "body": json.dumps({"body": body})}
    
    except (ClientError, json.JSONDecodeError) as error:
        # Lidando com possíveis erros
        error_message = f"An error occurred: {str(error)}"
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }
    
def check_existing_entry(phrase_hash):
    try:
        response = table.get_item(
            Key={
                'Id': phrase_hash
            }
        )
        if 'Item' in response:
            return response['Item']
        else:
            return None
    except ClientError as e:
        print(f"Error checking existing entry: {e}")
        return None
    
def v3_tts_description(event, context):
    try:
        # Extraindo a frase do event body
        dados = json.loads(event['body'])
        phrase = dados["phrase"]

        # Gerando o hash da frase para verificar se já existe no DynamoDB
        phrase_hash = hashlib.sha256(phrase.encode()).hexdigest()

        # Verificando se a entrada já existe no DynamoDB
        existing_entry = check_existing_entry(phrase_hash)

        if existing_entry:
            # Se a entrada existir, retornar os dados da entrada existente
            return {
                "statusCode": 200,
                "body": json.dumps(existing_entry)
            }
        else:
            # Se a entrada não existir, criar o áudio e gravar as referências
            response = polly.synthesize_speech(
                Text=phrase,
                OutputFormat='mp3',
                VoiceId='Camila',
                Engine='neural'
            )
            
            file = response['AudioStream']
            nome = f"{phrase_hash}.mp3" 

            # Adicionando o arquivo de áudio no novo bucket
            s3.upload_fileobj(file, os.getenv('BUCKET_NAME'), nome, ExtraArgs={'ACL': 'bucket-owner-full-control'})
            
            # Gerando a URL do áudio
            audio_url = f"https://{os.getenv('BUCKET_NAME')}.s3.amazonaws.com/{nome}"  

            # formatando a data de criação
            created_audio = now.strftime("%d-%m-%Y %H:%M:%S")

            # Salvando uma referência no DynamoDB
            table.put_item(
                Item={
                    'Id': phrase_hash,
                    'Phrase': phrase,
                    'AudioUrl': audio_url,
                    'CreatedAt': created_audio
                }
            )

            # Preparando o retorno
            body = {
                "received_phrase": phrase,
                "url_to_audio": audio_url,
                "created_audio": created_audio,
                "unique_id": phrase_hash
            }

            return {"statusCode": 200, "body": json.dumps({"body": body})}
    
    except (ClientError, json.JSONDecodeError) as error:
        # Lidando com possíveis erros
        error_message = f"An error occurred: {str(error)}"
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }
import json
import os
from datetime import datetime
from typing import Union

import boto3
import six
from google.cloud import translate_v2 as translate
from lambda_decorators import cors_headers


@cors_headers
def main(event, context):
    data = json.loads(event['body'])

    required_parameters = ['values', 'target_language']
    for parameter in required_parameters:
        if parameter not in data or not data[parameter]:
            return {
                "statusCode": 422,
                "body": json.dumps({"message": "'" + parameter + "' is required."})
            }
    if isinstance(data['values'], six.string_types) is not True:
        return {
            "statusCode": 422,
            "body": json.dumps({"message": "'values' should be string."})
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TRANSLATIONS'])

    result = table.get_item(Key={
        'text': data['values'],
        'targetLanguage': data['target_language']
    }).get('Item')

    if result is None or data.get('force') is True:
        translate_client = translate.Client()
        if isinstance(data['values'], six.binary_type):
            data['values'] = data['values'].decode('utf-8')
        try:
            response: Union[str, list, dict] = translate_client.translate(
                values=data['values'],
                target_language=data['target_language'],
                format_=data.get('format_'),
                source_language=data.get('source_language'),
                customization_ids=data.get('customization_ids'),
                model=data.get('model'))
        except ValueError:
            return {
                "statusCode": 422,
                "body": json.dumps({"message": "the number of values and translations differ"})
            }
        except:
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Failed to get translation."})
            }

        if result is None:
            timestamp = str(datetime.utcnow().timestamp())
            item = {
                'text': data['values'],
                'targetLanguage': data['target_language'],
                'detectedSourceLanguage': data.get('source_language') if response.get('detectedSourceLanguage') is None else response.get('detectedSourceLanguage'),
                'translatedText': response.get('translatedText'),
                'model': data.get('model'),
                'createdAt': timestamp,
                'updatedAt': timestamp
            }
            table.put_item(Item=item)

            result = item
        else:
            expression_attribute_names = {}
            expression_attribute_values = {}
            update_expression_items = []
            response['detectedSourceLanguage'] = data.get('source_language') if response.get('detectedSourceLanguage') is None else response.get('detectedSourceLanguage')
            for key in ['detectedSourceLanguage', 'translatedText', 'model']:
                if key in response and response.get(key) is not None:
                    result[key] = response.get(key)
                    expression_attribute_names['#k' + key] = key
                    expression_attribute_values[':v' + key] = response[key]
                    update_expression_items.append('#k' + key + ' = ' + ':v' + key)
            update_expression = 'SET ' + ','.join(update_expression_items)

            if len(update_expression_items) > 0:
                timestamp = str(datetime.utcnow().timestamp())
                expression_attribute_values[':updatedAt'] = timestamp
                update_expression = update_expression + ', updatedAt = :updatedAt'
                table.update_item(
                    Key={
                        'text': data['values'],
                        'targetLanguage': data['target_language']
                    },
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
                    UpdateExpression=update_expression,
                    ReturnValues='ALL_NEW',
                )

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }

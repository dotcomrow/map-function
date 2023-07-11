import json
from operator import methodcaller
from urllib.parse import unquote
import logging
import base64
import os
import geojson
from geojson import Polygon, FeatureCollection, LineString


logger = logging.getLogger(__name__)

def main_gcs(event):

    headers = {
            "Access-Control-Allow-Origin": "mapstuff.suncoast.systems",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
    }
    if event.method == "OPTIONS":
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        return ("", 204, headers)

    # Set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}

    try:
        # print('Raw Form Data: ' + unquote(base64.b64decode(event['body'])))
        # form = unquote(base64.b64decode(event['body']))
        # form_elements=form.split('&')
        # form = dict(map(methodcaller("split", "="), form_elements))

        # print('phone number detected as: ' + form['phoneNumber'])

        # dynamodb = boto3.resource('dynamodb')
        # msg_table = dynamodb.Table('MESSAGES')

            print('Query params: ' + str(event['queryStringParameters']))
            # response = msg_table.get_item(
            #     Key={'MESSAGE_ID': 'GREETING'})

            # greeting_msg = response['Item']['MESSAGE_TEXT']
            # print("Greeting message pulled from dynamodb: " + greeting_msg)
            
            
            
            params = event['queryStringParameters']
            features = []
            bbox = params['bbox']
            bboxArray = bbox.split(',')
            bboxStart = {
                'x' : float(bboxArray[0]),
                'y' : float(bboxArray[1])
            }
            bboxEnd = {
                'x' : float(bboxArray[2]),
                'y' : float(bboxArray[3])
            }
            
            graticuleParallels = params['graticuleParallels'].split(';')
            graticuleMeridians = params['graticuleMeridians'].split(';')
            
            graticuleParallels.insert(len(graticuleParallels), str(float(bboxEnd['x'])) + "," + str(float(bboxEnd['y'])) + "," + str(float(bboxStart['x'])) + "," + str(float(bboxEnd['y'])))
            graticuleParallels.insert(0, str(float(bboxStart['x'])) + "," + str(float(bboxStart['y'])) + "," + str(float(bboxEnd['x'])) + "," + str(float(bboxStart['y'])))
            
            graticuleMeridians.insert(len(graticuleMeridians), str(float(bboxEnd['x'])) + "," + str(float(bboxEnd['y'])) + "," + str(float(bboxEnd['x'])) + "," + str(float(bboxStart['y'])))
            # graticuleMeridians.insert(0, str(float(bboxStart['x'])) + "," + str(float(bboxStart['y'])) + "," + str(float(bboxStart['x'])) + "," + str(float(bboxEnd['y'])))
            
            i=0
            while i < len(graticuleParallels) - 1:
                parallelTopLine = graticuleParallels[i].split(',')
                parallelTopLineStart = {
                    'x' : float(parallelTopLine[0]),
                    'y' : float(parallelTopLine[1])
                }
                
                parallelTopLineEnd = {
                    'x' : float(parallelTopLine[2]),
                    'y' : float(parallelTopLine[3])
                }
                
                parallelBottomLine = graticuleParallels[i+1].split(',')
                parallelBottomLineStart = {
                    'x' : float(parallelBottomLine[0]),
                    'y' : float(parallelBottomLine[1])
                }
                
                parallelBottomLineEnd = {
                    'x' : float(parallelBottomLine[2]),
                    'y' : float(parallelBottomLine[3])
                }
                
                upperLeftPoint = {
                    'x' : bboxStart['x'],
                    'y' : parallelTopLineStart['y']
                }
                
                lowerLeftPoint = {
                    'x' : bboxStart['x'],
                    'y' : parallelBottomLineStart['y']
                }
                
                for meridians in graticuleMeridians:
                    meridianLine = meridians.split(',')
                    meridianLineStart = {
                        'x' : float(meridianLine[0]),
                        'y' : float(meridianLine[1])
                    }
                    
                    meridianLineEnd = {
                        'x' : float(meridianLine[2]),
                        'y' : float(meridianLine[3])
                    }
                    
                    upperRightPoint = {
                        'x' : meridianLineStart['x'],
                        'y' : upperLeftPoint['y']
                    }
                    
                    lowerRightPoint = {
                        'x' : meridianLineStart['x'],
                        'y' : lowerLeftPoint['y']    
                    }
                    
                    features.append(Polygon([[(upperLeftPoint['x'], upperLeftPoint['y']),
                                              (upperRightPoint['x'], upperRightPoint['y']),
                                              (lowerRightPoint['x'], lowerRightPoint['y']),
                                              (lowerLeftPoint['x'], lowerLeftPoint['y']),
                                              (upperLeftPoint['x'], upperLeftPoint['y'])]]))
                    
                    upperLeftPoint = upperRightPoint
                    lowerLeftPoint = lowerRightPoint
                    
                i+=1
            
            return (geojson.dumps(FeatureCollection(features)), 200, headers)

    except Exception as exception:
        print(exception)
        return {
            'statusCode': 500,
            'body': {
                "status": "ERROR",
                "details": exception
            },
            'headers': {
                "Content-Type": "application/json"
            }
        }

from flask_restful import Resource, reqparse
from PIL import Image
import requests
import json
import werkzeug


class ImageProcessing(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('image', location='files', type=werkzeug.FileStorage)
        args = parser.parse_args()
        args.get('image').save('unprocessed_image.jpg')
        unprocessed_image = Image.open("unprocessed_image.jpg")
        img = unprocessed_image.resize((544, 544), Image.ANTIALIAS)
        img.save("image.jpg")
        data = open('image.jpg', 'rb').read()

        return self._call_calorie_mama(data)

    def _call_calorie_mama(self, data):
        headers = {
            'Content-Type': 'image/jpeg',
        }
        r = requests.post(
            url='https://api-2445582032290.production.gw.apicast.io/v1/foodrecognition?user_key=369ff477f2803577f25128cab6d4749c',
            headers=headers,
            data=data)

        response_content = json.loads(r.content).get('results')

        # return top results
        num_results = min(len(response_content), 3)
        results = []

        for i in range(num_results):
            num_inner_results = min(len(response_content[i].get('items')), 3-i)
            for j in range(num_inner_results):
                serving_sizes = response_content[i].get('items')[j].get('servingSizes')
                if len(serving_sizes) > 1:
                    sorted_serving_sizes = sorted(serving_sizes, key=lambda k: k['servingWeight'], reverse=True)
                    serving_size = sorted_serving_sizes[0]
                else:
                    serving_size = serving_sizes[0]
                results.append({
                    'Item Type': response_content[i].get('items')[j].get('group'),
                    'Item': response_content[i].get('items')[j].get('name'),
                    'Serving size': serving_size.get('unit'),
                    'Score': response_content[i].get('items')[j].get('score'),
                })

        sorted_results = sorted(results, key=lambda k: k['Score'], reverse=True)
        return sorted_results[0:3]



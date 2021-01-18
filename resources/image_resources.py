from requests import get

from pathlib import Path

from flask_jwt import jwt_required

from flask_restful import Resource, reqparse

import cv2
import numpy as np

FILE_DIR = "Downloads"

class ImageResources(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('first_image_url',
                        type = str,
                        required = True,
                        help = "The first image URL cannot be blank."
                        )

    parser.add_argument('second_image_url',
                        type = str,
                        required = True,
                        help = "The Second image URL cannot be blank."
                        )

    @jwt_required()
    def get(self):
        URLs = ImageResources.parser.parse_args()
        first_image_url = URLs['first_image_url']
        second_image_url = URLs['second_image_url']

        image1_file = get(first_image_url)
        image2_file = get(second_image_url)
        if image1_file.status_code != 200 or \
                image2_file.status_code != 200:
            return {'message' : 'The url of image files does not exist.' }, 404

        home_path = str(Path.home())
        image_file_path = home_path + '/' + FILE_DIR + '/'

        open(image_file_path + '1.jpg', 'wb').write(image1_file.content)
        open(image_file_path + '2.jpg', 'wb').write(image2_file.content)

        original = cv2.imread(image_file_path + "1.jpg")
        image_to_compare = cv2.imread(image_file_path + "2.jpg")
        # Check if 2 images are the same
        if original.shape == image_to_compare.shape:
            # The images have same size and channels
            difference = cv2.subtract(original, image_to_compare)
            b, g, r = cv2.split(difference)

            if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
                return {'message' : 'A percentage of 2 images are: 100%.' }, 200

        sift = cv2.xfeatures2d.SIFT_create()
        kp_1, desc_1 = sift.detectAndCompute(original, None)
        kp_2, desc_2 = sift.detectAndCompute(image_to_compare, None)

        index_params = dict(algorithm=0, trees=5)
        search_params = dict()
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(desc_1, desc_2, k=2)

        good_points = []
        for m, n in matches:
            if m.distance < 0.6 * n.distance:
                good_points.append(m)

        # Define how similar they are
        number_keypoints = 0
        if len(kp_1) <= len(kp_2):
            number_keypoints = len(kp_1)
        else:
            number_keypoints = len(kp_2)

        return {'message' : 'A percentage of 2 images are: ' + str(round(len(good_points) / number_keypoints * 100, 2)) + '%.'}, 200


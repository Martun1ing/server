from flask import jsonify
from matplotlib import cm

import hashing_helper
from holographic import *
from io import BytesIO
from os import listdir
from os.path import isfile, join
import base64
from flask import Flask
from flask_restful import Api, Resource, request
from config import Config
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'super_useful_key'
# load settings from the config.py
app.config.from_object(Config)
CORS(app)

api = Api(app)


class list_image(Resource):
    def get(self):
        fichiers = [f for f in listdir('stockage/zeros') if isfile(join('stockage/zeros', f))]
        return jsonify(fichiers)


class file_upload(Resource):
    def post(self):
        file = request.files['file']
        filename = secure_filename(file.filename)
        index = filename.rfind(".")
        filename = filename[:index]
        json_path = os.path.join('temp', 'temp.json')
        FaceReconHelper = FaceReconHelperClassBuilder(json_path)
        FaceReconHelper.GenerateDescriptor(filename, image_path=file)
        # # le user descriptor sera soit envoyé sur le client soit sur un deuxième serveur
        # return jsonify({"user_descriptor": str(user_descriptor)})

    def hash(unknown_descriptor):
        salt1, descriptor_hash, user_descriptor, salt2, user_descriptor_hash, server_descriptor = hashing_helper.split_and_hash_descriptor(
            unknown_descriptor)
        b = server_descriptor, user_descriptor
        return b

class recombine(Resource):
    def recombineTest(filename, server_descriptor, user_descriptor):
        Descriptor = []
        for i in range(len(user_descriptor)):
            Descriptor = Descriptor + (
                hashing_helper.RecombineDescriptors(user_descriptor[i], server_descriptor[i])).tolist()
        myFileA = open("stockage/zeros/" + filename, "r")
        a = int(myFileA.read())
        myFileA.close()
        return recombine.suppr0(Descriptor, a)

    @staticmethod
    def suppr0(lst, nbr0):
        """supprime les zeros en trop"""
        a = len(lst) - 1
        while nbr0 > 0:
            lst.pop(a)
            a = a - 1
            nbr0 = nbr0 - 1
        return lst

    def arrondi(lst):
        for i in range(len(lst)):
            if lst[i] < 0:
                lst[i] = 0
            if lst[i] > 255:
                lst[i] = 255
        return lst

    def recombine_RGB(filename, lstr, lstg, lstb):
        """recombine les 3 canaux de l'image"""
        myFileA = open("stockage/shape/" + 's' + filename, "r")
        b = eval(myFileA.read())
        myFileA.close()
        a = len(lstr) - 1
        lstrgb = []
        while a > -1:
            lstrgb.append(lstb[a])
            lstrgb.append(lstg[a])
            lstrgb.append(lstr[a])
            a = a - 1
        lstrgb.reverse()
        lstrgb = np.multiply(lstrgb, 255)
        lstrgb = [int(round(num, 0)) for num in lstrgb]
        lstrgb = recombine.arrondi(lstrgb)
        lstrgb = np.array(lstrgb).reshape(b)
        lstrgb = lstrgb.astype(np.uint8)
        return lstrgb

    @staticmethod
    def post():
        filename = request.form.get('filename')
        myFileR = open("stockage/user_descriptor/" + 'R' + filename, "r")
        user_descriptor = eval(myFileR.read())
        myFileR.close()
        myFile1R = open("stockage/server_descriptor/" + 'R' + filename, "r")
        server_descriptor = eval(myFile1R.read())
        myFile1R.close()
        r = recombine.recombineTest(filename, user_descriptor, server_descriptor)
        myFileG = open("stockage/user_descriptor/" + 'G' + filename, "r")
        user_descriptor = eval(myFileG.read())
        myFileG.close()
        myFile1G = open("stockage/server_descriptor/" + 'G' + filename, "r")
        server_descriptor = eval(myFile1G.read())
        myFile1G.close()
        g = recombine.recombineTest(filename, user_descriptor, server_descriptor)
        myFileB = open("stockage/user_descriptor/" + 'B' + filename, "r")
        user_descriptor = eval(myFileB.read())
        myFileB.close()
        myFile1B = open("stockage/server_descriptor/" + 'B' + filename, "r")
        server_descriptor = eval(myFile1B.read())
        myFile1B.close()
        b = recombine.recombineTest(filename, user_descriptor, server_descriptor)
        im = recombine.recombine_RGB(filename, r, g, b)
        print(im)
        image = Image.fromarray(im)
        image.show()
        image = im.astype(np.uint8)
        # convert picture to base64
        img_str = base64.b64encode(image)
        base_image = img_str.decode()
        #base_image = 'iVBORw0KGgoAAAANSUhEUgAAAAoAAAAQCAYAAAAvf+5AAAAAAXNSR0IB2cksfwAAAiFJREFUKJElyDtME3EAwOFf767Xu9Jrr/Vq+hAiRBcGEtFBNiVRB42TTk7E6OaumxthMS5OxrgYddEJNcb4AjVIkGq18ioJIG21xV5LW9rr4/4OfuPneTf9QGS+rXA40mCfpbFaDrDf1JA0E58io6gamq6jxA4kUP6mKKZvodeDVBsX0GoWsX6dbLmOvzaH6k8iyV4fZsQinBzF8Yxj6mG25tLYqQxDyUEGzD/YlV0kjxC06xVMU2alEWO3UMJRIJNdx90r03QCDAwlkXpuD0ns0W6rvMgn2Gn00bX/oAUibORybFa9DMQNJEXyYPjabJXjTNte2oEAO3aJotdi8nuQ+c1+3I6DZFcqPJ9d4tViAZ7ew5FdEqcv0TT6aDhdMmWDQkVFSS9luXZ7BrQEdPNM3nnE9YkTNGsV1HSJmk+n5Z5HEb0eACODOum1CDTzZJe+Iik6dqnAWjHPz1/jyMNx/80PiyuoikLY08HnN6hWCmzndsl1NEYCGrKuoyidOgDNnuDi6CFC8X6a1kFmZj9CaoHo0WMsL6RQLCsGgCpcZpe3CW0XOXJqiEjk/7/+sgCA58ndKTH18CXzb99AKArVEgBjYycxNJXVcpczwxpSeHAYH10Akn6ZsBEGwBUu6z9SHB8/y+WrV+DT5/cCENAnzFBQgEcYAVPIslcA4tzEDbGxmRVSzbYBMK0grWYLSVJpOQ7RaJSgpvPs/mN2Sr/5B1sd5FBeG/M6AAAAAElFTkSuQmCC'
        return jsonify(base_image)


api.add_resource(list_image, "/api/list_image")
api.add_resource(recombine, '/api/recombine')
api.add_resource(file_upload, "/api/file_upload")

if __name__ == "__main__":
    app.run(host="localhost", port=4000)

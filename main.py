import numpy as np
from flask import Flask, session, redirect, url_for, escape, request, jsonify
from flask_restful import Resource, Api

import hashing_helper
from hashing_helper import *
from werkzeug.utils import secure_filename
import json
from holographic import *
import os
import pickle
from io import BytesIO
from matplotlib import cm
from os import listdir
from os.path import isfile, join
import random
import string
import base64
from config import Config
from PIL import Image
from flask_cors import CORS
import shutil
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
        fichiers = [f for f in listdir('server_descriptor') if isfile(join('server_descriptor', f))]
        return jsonify({'name_picture': fichiers})

class file_upload(Resource):
    def post(self):
        file = request.files['file']
        filename = secure_filename(file.filename)
        index = filename.rfind(".")
        filename = filename[:index]
        json_path = os.path.join('temp', 'temp.json')
        FaceReconHelper = FaceReconHelperClassBuilder(json_path)
        FaceReconHelper.GenerateDescriptor(image_path=file)
        #salt1, descriptor_hash, user_descriptor, salt2, user_descriptor_hash, server_descriptor = split_and_hash_descriptor(unknown_descriptor)

        # user_descriptor, server_descriptor = a
        # myFile = open("user_descriptor/" + filename, "wb+")
        # myFile.write(user_descriptor)
        # myFile.close()
        # myFile2 = open("server_descriptor/" + filename, "wb+")
        # myFile2.write(server_descriptor)
        # myFile2.close()
        # # Test uniquement, permet d'avoir un résultat rapide
        # #self.reombineTest(user_descriptor, server_descriptor)
        # user_descriptor = eval(user_descriptor.decode())
        # server_descriptor = eval(server_descriptor.decode())
        # # le user descriptor sera soit envoyé sur le client soit sur un deuxième serveur
        # return jsonify({"user_descriptor": str(user_descriptor)})

    def hash(unknown_descriptor):
        print('i')
        salt1, descriptor_hash, user_descriptor, salt2, user_descriptor_hash, server_descriptor = hashing_helper.split_and_hash_descriptor(
            unknown_descriptor)
        a = server_descriptor, user_descriptor
        return a



    # Test uniquement, permet d'avoir un résultat rapide
    def reombineTest(self, user_descriptor, server_descriptor):
        DescriptorRec = RecombineDescriptors(user_descriptor, server_descriptor)
        # transformation du DescriptorRec en image PNG
        im = Image.fromarray(np.uint8(cm.gist_earth(DescriptorRec) * 255))
        im.show()

class recombine(Resource):

    def suppr0(self, lst, nbr0):
        '''supprime les zeros en trop'''
        a = len(lst) - 1
        while nbr0 > 0:
            lst.pop(a)
            a = a - 1
            nbr0 = nbr0 - 1
        return lst

    def recombine_RGB(self, lstr, lstg, lstb, nbr0):
        '''recombine les 3 canaux de l'image et enlève les 0'''
        self.suppr0(lstr, nbr0)
        self.suppr0(lstg, nbr0)
        self.suppr0(lstb, nbr0)

        a = len(lstr) - 1
        lstrgb = []
        while a > -1:
            lstrgb.append(lstb[a])
            lstrgb.append(lstg[a])
            lstrgb.append(lstr[a])
            a = a - 1
        lstrgb.reverse()
        return lstrgb

    def post(self):
        filename1 = request.form.get('filename')
        # création du dossier contenant le json
        folder = 'temp'
        json_path = os.path.join(folder, 'temp.json')
        FaceReconHelper = FaceReconHelperClassBuilder(json_path)

        # préparation des descriptors à la recombinaison
        user_descriptor1 = open("user_descriptor/" + filename1, 'rb')
        server_descriptor1 = open("server_descriptor/" + filename1, 'rb')
        user_descriptor1 = user_descriptor1.read()
        server_descriptor1 = server_descriptor1.read()
        user_descriptor1 = eval(user_descriptor1.decode())
        server_descriptor1 = eval(server_descriptor1.decode())

        # recombinaison
        DescriptorRec = RecombineDescriptors(user_descriptor1, server_descriptor1)
        FaceReconHelper.LoadKnownDescriptor(DescriptorRec)

        # transformation du DescriptorRec en image PNG
        im = Image.fromarray(np.uint8(cm.gist_earth(DescriptorRec) * 255))
        # im.show()

        # convert picture to base64
        buffered = BytesIO()
        im.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        base_image = "data:image/jpeg;base64," + img_str.decode()
        return jsonify('test', base_image)

api.add_resource(list_image, "/api/list_image")
api.add_resource(recombine, '/api/recombine')
api.add_resource(file_upload, "/api/file_upload")

if __name__ == "__main__":
    app.run(host="localhost", port=4000)

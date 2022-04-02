import os
import json
from PIL import Image
import PIL.Image
import numpy as np

from main import file_upload, recombine


class FaceReconHelperClassBuilder:
    def __init__(self, json_path='temp/temp.json'):
        self.json_path = json_path
        if not os.path.exists(self.json_path):
            data = {"known_descriptor": [], "unknown_descriptors": [], "match_distances": [], "match_result": False}
            with open(self.json_path, 'w+') as file:
                json.dump(data, file)

    def GenerateDescriptor(self, filename, image_path='image.jpg'):
        im = PIL.Image.open(image_path)
        im = im.convert('RGB')
        image = np.array(im)
        b = image.shape
        myFileA = open("stockage/shape/" + 's' + filename, "w+")
        myFileA.write(str(b))
        myFileA.close()
        e = 0
        descriptor_R2 = []
        descriptor_G2 = []
        descriptor_B2 = []
        descriptor_R = []
        descriptor_G = []
        descriptor_B = []
        for f in image:
            e += 1
            red = []
            green = []
            blue = []
            for j in range(3):
                for i in range(len(f)):
                    if j == 0:
                        red.append(f[i][j])
                    if j == 1:
                        green.append(f[i][j])
                    if j == 2:
                        blue.append(f[i][j])
            descriptor_R = descriptor_R + red
            descriptor_G = descriptor_G + green
            descriptor_B = descriptor_B + blue
        descriptor_R2 = descriptor_R2 + descriptor_R
        descriptor_G2 = descriptor_G2 + descriptor_G
        descriptor_B2 = descriptor_B2 + descriptor_B
        a = int(128 - ((len(descriptor_R2) / 128 - int(len(descriptor_R2) / 128)) * 128))
        myFileA = open("stockage/zeros/" + filename, "w+")
        myFileA.write(str(a))
        myFileA.close()
        descriptor_R2 = self.zero_add(descriptor_R2, a)
        descriptor_R2 = np.divide(descriptor_R2, 256)
        descriptor_G2 = self.zero_add(descriptor_G2, a)
        descriptor_G2 = np.divide(descriptor_G2, 256)
        descriptor_B2 = self.zero_add(descriptor_B2, a)
        descriptor_B2 = np.divide(descriptor_B2, 256)
        descriptor_R2 = self.tri4(descriptor_R2)
        descriptor_G2 = self.tri4(descriptor_G2)
        descriptor_B2 = self.tri4(descriptor_B2)
        xR = []
        yR = []
        xG = []
        yG = []
        xB = []
        yB = []

        print('Wait...')
        for unknown_descriptor in descriptor_R2:
            server_descriptor_R, user_descriptor_R = file_upload.hash(unknown_descriptor)
            xR.append(eval(server_descriptor_R))
            yR.append(eval(user_descriptor_R))
        print('R')
        # r = recombine.recombineTest(filename, xR, yR)
        for unknown_descriptor in descriptor_G2:
            server_descriptor_G, user_descriptor_G = file_upload.hash(unknown_descriptor)
            xG.append(eval(server_descriptor_G))
            yG.append(eval(user_descriptor_G))
        print('G')
        #g = recombine.recombineTest(filename, xG, yG)
        for unknown_descriptor in descriptor_B2:
            server_descriptor_B, user_descriptor_B = file_upload.hash(unknown_descriptor)
            xB.append(eval(server_descriptor_B))
            yB.append(eval(user_descriptor_B))
        print('B')
        # b = recombine.recombineTest(filename, xB, yB)
        # recombine.recombine_RGB(filename, r, g, b)
        myFileR = open("stockage/user_descriptor/" + 'R' + filename, "w+")
        myFileR.write(str(xR))
        myFileR.close()
        myFile1R = open("stockage/server_descriptor/" + 'R' + filename, "w+")
        myFile1R.write(str(yR))
        myFile1R.close()

        myFileG = open("stockage/user_descriptor/" + 'G' + filename, "w+")
        myFileG.write(str(xG))
        myFileG.close()
        myFile1G = open("stockage/server_descriptor/" + 'G' + filename, "w+")
        myFile1G.write(str(yG))
        myFile1G.close()

        myFileB = open("stockage/user_descriptor/" + 'B' + filename, "w+")
        myFileB.write(str(xB))
        myFileB.close()
        myFile1B = open("stockage/server_descriptor/" + 'B' + filename, "w+")
        myFile1B.write(str(yB))
        myFile1B.close()

    @staticmethod
    def zero_add(lst, a):
        """transforme la liste pour que sa longueur soit un multiple de 128"""
        lst0 = lst
        while a > 0:
            lst0.append(0)
            a = a - 1
        return lst0

    @staticmethod
    def tri4(lst):
        """divise une liste en liste de b élément"""
        a = len(lst)
        # nombre d'élément dans les listes
        b = 128
        lst_dec = []
        while a > 0:
            lst_dec.append(lst[a - b:a])
            a = a - b
        lst_dec.reverse()
        return lst_dec

    def load_json_file(self):
        with open(self.json_path, 'r') as file:
            self.data = json.load(file)
            # have to convert everything to np.ndarray
            self.data['unknown_descriptors'] = [np.array(a) for a in self.data['unknown_descriptors']]
            self.data['known_descriptor'] = np.array(self.data['known_descriptor'])
            self.data['match_distances'] = np.array(self.data['match_distances'])

    def save_json_file(self):
        with open(self.json_path, 'w') as file:
            # convert everything back to list before saving
            self.data['unknown_descriptors'] = [a.tolist() for a in self.data['unknown_descriptors']]
            self.data['known_descriptor'] = self.data['known_descriptor'].tolist()
            self.data['match_distances'] = self.data['match_distances'].tolist()
            json.dump(self.data, file)

    def LoadKnownDescriptor(self, known_descriptor):
        # if self.ValidateDescriptor(known_descriptor):
        self.load_json_file()
        self.data['known_descriptor'] = np.array(known_descriptor)
        self.save_json_file()

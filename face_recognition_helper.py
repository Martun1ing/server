import os
import json

import PIL.Image
import numpy as np

from main import file_upload


class FaceReconHelperClassBuilder:
    def __init__(self, json_path='temp/temp.json'):
        self.json_path = json_path
        if not os.path.exists(self.json_path):
            data = {"known_descriptor": [], "unknown_descriptors": [], "match_distances": [], "match_result": False}
            with open(self.json_path, 'w+') as file:
                json.dump(data, file)

    def tri4(self, lst):
        '''divise une liste en liste de b élément'''
        a = len(lst)
        # nombre d'élément dans les listes
        b = 128
        lst_dec = []
        while a > 0:
            lst_dec.append(lst[a - b:a])
            a = a - b
        lst_dec.reverse()
        return lst_dec

    def zero_add(self, lst, a):
        '''transforme la liste pour que sa longueur soit un multiple de 128'''
        b = a
        lst0 = lst
        while a > 0:
            lst0.append(0)
            a = a - 1
        return lst0

    def GenerateDescriptor(self, image_path='image.jpg'):
        im = PIL.Image.open(image_path)
        image = np.array(im)
        # image = [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]]
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
        a = int(128-((len(descriptor_R2)/128 - int(len(descriptor_R2)/128))*128))
        descriptor_R2 = self.zero_add(descriptor_R2, a)
        descriptor_G2 = self.zero_add(descriptor_G2, a)
        descriptor_B2 = self.zero_add(descriptor_B2, a)
        descriptor_R2 = self.tri4(descriptor_R2)
        descriptor_G2 = self.tri4(descriptor_G2)
        descriptor_B2 = self.tri4(descriptor_B2)
        print(len(descriptor_B2))
        x = []
        y = []
        for unknown_descriptor in descriptor_B2:
            server_descriptor, user_descriptor = file_upload.hash(unknown_descriptor)
            x = x + server_descriptor
            y = y + server_descriptor

        # for unknown_descriptor in descriptor_G2:
        #     file_upload.hash(unknown_descriptor)
        # for unknown_descriptor in descriptor_R2:
        #     file_upload.hash(unknown_descriptor)
        print('OOO?IGH')
        myFile4 = open("user_descriptor/" + 'user_descriptor', "wb+")
        myFile4.write(str(user_descriptor).encode())
        myFile4.close()
        myFile5 = open("descriptor_RGB2/" + 'descriptor_G2', "wb+")
        myFile5.write(str(descriptor_G2).encode())
        myFile5.close()
        myFile6 = open("descriptor_RGB2/" + 'descriptor_B2', "wb+")
        myFile6.write(str(descriptor_B2).encode())
        myFile6.close()

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
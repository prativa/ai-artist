from torch.utils.data.dataset import Dataset

import numpy as np
import imageio
import torch
from torchvision import transforms
import os

"""
https://www.cbica.upenn.edu/sbia/Spyridon.Bakas/MICCAI_BraTS/2018/MICCAI_BraTS_2018_Data_Training.zip 
"""

class BratsDataset(Dataset):
    """
    mode= train, validation, test
    """
    def __init__(self, mode='train'):
        loader = DataReaderBrats()
        self.train=np.asarray(loader.get_train_files())
        self.test=np.asarray(loader.get_test_files())
        self.mode = mode
        self.transforms = transforms.Compose(
            [transforms.ToTensor()])

    def __getitem__(self, index):

            if self.mode == 'train':
                train_x, train_y = self.train
                img = imageio.imread(train_x[index])
                img=img.astype(np.float32)/255
                #print(img.shape)
                data = torch.from_numpy(img.reshape(1,240,240))

                mask = imageio.imread(train_y[index])
                mask=mask.astype(np.float32)/255
                mask_data=torch.from_numpy(mask)
                #data_mask = self.transforms(mask_img)

                return (data, mask_data)
            elif self.mode == 'validation':
                valid_x, valid_y, labels = self.validation
                return valid_x[index], valid_y[index]
            else:
                test_x, test_y = self.test
                img = imageio.imread(test_x[index])
                img = img.astype(np.float32)/255
                data = torch.from_numpy(img.reshape(1,240,240))

                return (data, 1)


    def __len__(self):
        if self.mode == 'train':
            train_x, train_y = self.train
            return len(train_x)
        elif self.mode == 'validation':
            valid_x, valid_y, labels = self.validation
            return len(valid_x)
        else:
            test_x, test_y= self.test
            return len(test_x)


class DataReaderBrats(object):

    def __init__(self):
        self.data_dir = "/home/milton/dataset/segmentation/BRATS/BRATS2015/training/images"
        self.train_dir = os.path.join(self.data_dir, "flair")
        self.test_dir = "/home/milton/dataset/segmentation/BRATS/BRATS2015/testing/images"
        self.train_masks_dir = os.path.join(self.data_dir, "labels")
        self.num_channels = 1
        self.image_height = 1280
        self.image_width = 1918
        self.num_classes = 2
        self.num_threads = 4

    def get_train_files(self):
       train_files=[]
       train_mask_files=[]
       for file_name in os.listdir(self.train_dir):
           file_path = os.path.join(self.train_dir, file_name)
           train_files.append(file_path)
           mask_file = os.path.join(self.train_masks_dir, file_name)
           train_mask_files.append(mask_file)
       print("Total train {}".format(len(train_files)))
       return train_files, train_mask_files

    def get_test_files(self):
       test_files=[]
       train_mask_files=[]
       for file_name in os.listdir(self.test_dir):
           file_path = os.path.join(self.test_dir, file_name)
           test_files.append(file_path)
           #mask_file = os.path.join(self.masks_dir, os.path.basename(file_path),".gif")
           #train_mask_files.append(mask_file)
       print(len(test_files))
       return test_files, 1






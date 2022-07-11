import os
from pathlib import Path

import sys
import pandas as pd
import numpy as np
from PIL import Image
import fnmatch
import nibabel as nib


class Constant:
    ABS_PATH = os.path.dirname(os.path.abspath('__file__' + "/../../"))
    DATA_PATH = os.path.join(ABS_PATH, 'data/Seg_Data')
    NIFTI_PATH = 'matrices1.00'


class DataBlock(Constant):
    def __init__(self):
        self.data_dir = os.path.join(Constant.ABS_PATH, Constant.DATA_PATH)
        self.patient_dataframe = None
        self.initialize()

    def initialize(self):
        self.initialize_patient_dataframe()
        self.get_nifti_files()
        self.add_png()

    def initialize_patient_dataframe(self):
        children = [os.path.join(self.data_dir, child) for child in os.listdir(self.data_dir)]
        directories = filter(os.path.isdir, children)
        self.patient_dataframe = pd.DataFrame(directories, columns=['PatientID'])

    def get_nifti_files(self):
        """
        """
        for idx, patient in enumerate(self.patient_dataframe.PatientID):
            patient_nifti_dir = os.path.join(patient, Constant.NIFTI_PATH)
            self.patient_dataframe.at[idx, 'T2_Axial'] = \
                fnmatch.filter(os.listdir(patient_nifti_dir), '*T2_Axial.nii.gz')[0]
            self.patient_dataframe.at[idx, 'Prostate'] = \
                fnmatch.filter(os.listdir(patient_nifti_dir), '*prostate.nii.gz')[0]
            self.patient_dataframe.at[idx, 'SV'] = fnmatch.filter(os.listdir(patient_nifti_dir), '*sv.nii.gz')[0]
            self.patient_dataframe.at[idx, 'TZ'] = fnmatch.filter(os.listdir(patient_nifti_dir), '*tz.nii.gz')[0]

    @staticmethod
    def convert_to_png(scan, save_directory, column):
        patient_id = save_directory.split('/')[-4].lower()

        img_fdata = scan.get_fdata()
        for idx in range(scan.shape[2]):

            slice_number = img_fdata[:, :, idx]

            img = Image.fromarray(slice_number).convert("L")
            if idx < 10:
                img.save(os.path.join(save_directory, f'{patient_id}_{column}_0{idx}.png'))
            else:
                img.save(os.path.join(save_directory, f'{patient_id}_{column}_{idx}.png'))

        return patient_id

    def add_png(self):
        """
        """
        for patient_idx in range(self.patient_dataframe.shape[0]):
            for column in self.patient_dataframe.columns:
                if 'PatientID' not in column and '_png' not in column:

                    save_directory = os.path.join(self.patient_dataframe.PatientID[patient_idx], '../..',
                                                  column.lower())

                    image_directory = os.path.join(self.patient_dataframe.PatientID[patient_idx], Constant.NIFTI_PATH)

                    file_path = os.path.join(image_directory, self.patient_dataframe[column][patient_idx])
                    scan = nib.load(file_path)
                    patient_id = self.convert_to_png(scan, save_directory, column)

                    match: str = f'{patient_id}*.png'
                    column_name = f'{column}_png'
                    self.patient_dataframe.at[patient_idx, column_name] = str(fnmatch.filter(os.listdir(
                        save_directory), match))


if __name__ == '__main__':
    data = DataBlock()

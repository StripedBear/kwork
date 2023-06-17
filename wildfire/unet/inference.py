import os
import pandas as pd

from generator import *
from model import *
from metrics import *

import time

start = time.time()

N_FILTERS = 16
N_CHANNELS = 3

IMAGE_SIZE = (256, 256)
MODEL_NAME = 'unet'

RANDOM_STATE = 42

IMAGES_PATH = '../../dataset/images/patches/'
MASKS_PATH = '../../dataset/masks/patches/'

IMAGES_CSV = './dataset/images_test.csv'
MASKS_CSV = './dataset/masks_test.csv'

OUTPUT_DIR = './log'
OUTPUT_CSV_FILE = 'output_v1_{}.csv'.format(MODEL_NAME)
WRITE_OUTPUT = True

WEIGHTS_FILE = './train_output/model_unet_small_Murphy_final_weights_v3.h5'

TH_FIRE = 0.53


if not os.path.exists(os.path.join(OUTPUT_DIR, MODEL_NAME, 'arrays')):
    os.makedirs(os.path.join(OUTPUT_DIR, MODEL_NAME, 'arrays'))


try:
    np.random.bit_generator = np.random._bit_generator
except:
    pass

images_df = pd.read_csv(IMAGES_CSV)
masks_df = pd.read_csv(MASKS_CSV)


print('Loading images...')
images = []
masks = []

images = [ os.path.join(IMAGES_PATH, image) for image in images_df['images'] ]
masks = [ os.path.join(MASKS_PATH, mask) for mask in masks_df['masks'] ]

model = get_model(MODEL_NAME, input_height=IMAGE_SIZE[0], input_width=IMAGE_SIZE[1], n_filters=N_FILTERS, n_channels=N_CHANNELS)

model.summary()

print('Loading weghts...')
model.load_weights(WEIGHTS_FILE)
print('Weights Loaded')


print('# of Images: {}'.format( len(images)) )
print('# of Masks: {}'.format( len(masks)) )

step = 0
steps = len(images)
for image, mask in zip(images, masks):
    
    try:
        
        # img = get_img_arr(image)
        img = get_img_762bands(image)
        
        mask_name = os.path.splitext(os.path.basename(mask))[0]
        image_name = os.path.splitext(os.path.basename(image))[0]
        mask = get_mask_arr(mask)

        txt_mask_path = os.path.join(OUTPUT_DIR, MODEL_NAME, 'arrays', 'grd_' + mask_name + '.txt')
        txt_pred_path = os.path.join(OUTPUT_DIR, MODEL_NAME, 'arrays', 'det_' + image_name + '.txt')

        y_pred = model.predict(np.array( [img] ), batch_size=1)

        y_true = mask[:,:,0] > TH_FIRE
        y_pred = y_pred[0, :, :, 0] > TH_FIRE


        np.savetxt(txt_mask_path, y_true.astype(int), fmt='%i')
        np.savetxt(txt_pred_path, y_pred.astype(int), fmt='%i')

        step += 1
        
        if step%100 == 0:
            print('Step {} of {}'.format(step, steps)) 
            
    except Exception as e:
        print(e)
        
        with open(os.path.join(OUTPUT_DIR, "error_log_inference.txt"), "a+") as myfile:
            myfile.write(str(e))
    

print('Done!')

import os
from model import *
from generator import *
import cv2

IMAGE_NAME = 'LC08_L1TP_117016_20200926_20200926_01_RT_p00214.tif'

IMAGE_PATH = '../../dataset/landsat_patches/'
OUTPUT_PATH = 'output'

MODEL_NAME = 'unet'

N_FILTERS = 16
N_CHANNELS = 3

IMAGE_SIZE = (256, 256)

WEIGHTS_FILE = 'train_output/model_unet_Schroeder_final_weights.h5'

TH_FIRE = 0.25

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

model = get_model(MODEL_NAME, input_height=IMAGE_SIZE[0], input_width=IMAGE_SIZE[1], n_filters=N_FILTERS, n_channels=N_CHANNELS)
#model.summary()

print('Loading weghts...')
model.load_weights(WEIGHTS_FILE)
print('Weights Loaded')

img_path = os.path.join(IMAGE_PATH, IMAGE_NAME)

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

print('IMAGE: {}'.format(img_path))

img = get_img_762bands(img_path)

y_pred = model.predict(np.array( [img] ), batch_size=1)
y_pred = y_pred[0, :, :, 0] > TH_FIRE

y_pred = np.array(y_pred * 255, dtype=np.uint8)

output_image = os.path.join(OUTPUT_PATH, IMAGE_NAME)
cv2.imwrite(output_image, cv2.cvtColor(y_pred, cv2.COLOR_RGB2BGR))

OUTPUT_DIR = 'output'
OUTPUT_IMAGE_NAME = IMAGE_NAME.split('.')[0] + '.png'


img = np.array(img * 255, dtype=np.uint8)
cv2.imwrite(os.path.join(OUTPUT_DIR, OUTPUT_IMAGE_NAME), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

print('Done!')

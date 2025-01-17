
# ##### Parameters #####
BATCH				= 8
IMG_WIDTH			= int(260 / 2)
IMG_HEIGHT			= int(228 / 2)
INPUT_SHAPE			= (IMG_WIDTH, IMG_HEIGHT)
SEED				= 3141
BANDS				= 6
MAX_FREQUENCY		= 10
VALIDATION_SPLIT	= 0.2
EPOCHS				= 10
LATENT_ARRAY_SIZE	= 64 # Paper uses 512
BYTE_ARRAY_SIZE		= IMG_HEIGHT * IMG_WIDTH
CHANNEL				= (2 * BANDS + 1)
PROJECTION			= 2 * (2 * BANDS + 1) + 1
QKV_DIM				= PROJECTION
LEARNING_RATE		= 0.0015
WEIGHT_DECAY_RATE	= 0.0001
DROPOUT_RATE		= 0.1
TRANSFOMER_NUM		= 4
HEAD_NUM			= 4
MODULES_NUM			= 4
ITERATIONS			= 4
OUT_SIZE			= 1 # binary as only left or right knee

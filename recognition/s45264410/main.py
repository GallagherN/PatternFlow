import tensorflow as tf
from driver import pre_process
from keras.layers import Input
from tensorflow.keras.optimizers import Adam
IMG_WIDTH = 256
IMG_HEIGHT = 192
IMG_CHANNELS = 3

def main():
    print(tf.__version__)
    # use batch size of 1 to save VRAM
    BATCH_SIZE = 2

    # TensorFlow provided code to limit GPU memory growth
    # Retrieved from:
    # https://www.tensorflow.org/guide/gpu
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            # Currently, memory growth needs to be the same across GPUs
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            # Memory growth must be set before GPUs have been initialized
            print(e)
    model = pre_process()
    model.load_data()
    # model.visualise_loaded_data()
    input = Input((IMG_WIDTH, IMG_HEIGHT, IMG_CHANNELS))
    model.Unet(input_img=input)
    model.model.summary()
    learning_rate = 0.001
    epochs = 5000
    decay_rate = learning_rate / epochs
    model.model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.00001),
                        loss=pre_process.dice_loss,
                        metrics=pre_process.dice_coefficient)
    # model.show_predictions()  # sanity check

    history = model.model.fit(x=model.train_ds.batch(BATCH_SIZE),
                              validation_data=model.val_ds.batch(BATCH_SIZE),
                              epochs=10)
    model.show_predictions()

    # Get dice similarity for test set and show result
    print("Evaluate")
    result = model.model.evaluate(model.test_ds.batch(BATCH_SIZE))
    print(dict(zip(model.model.metrics_names,result)))

    print("END")
    
if __name__ == "__main__":
    main()
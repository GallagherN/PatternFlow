import tensorflow as tf
import tensorflow.keras as tfk

class VectorQuantizer(tfk.layers.Layer):
    def __init__(self, n_embeddings, embedding_dim, beta, **kwargs):
        super().__init__(**kwargs)
        self.embedding_dim = embedding_dim
        self.n_embeddings = n_embeddings
        self.beta = beta 
        self.embeddings = tf.Variable(
            initial_value = tf.random_uniform_initializer()(
                shape=(self.n_embeddings, self.embedding_dim), dtype='float32'
            ),
            trainable=True,
            name='codebook_vectors'
        )

    def call(self, x):
        '''
            This function takes the (HxWxC) encoded image then maps each C-dim pixel vector to the closest embedding C-dim vector defined in the codebook
        '''
        input_shape = tf.shape(x)
        pixel_vectors = tf.reshape(x, [-1, self.embedding_dim]) # The shape of the input now becomes (H*W, C)
        
        #### Quantization - Replace each pixel vector by its closest embedding in the codebook
        # Get the code of the closest vector in the codebook for each pixel vector
        quantized_codes = self.get_closest_codes(pixel_vectors) # The shape of quantized_codes should be (H*W, 1)
        one_hot_encoddings = tf.one_hot(quantized_codes, self.n_embeddings) # Express each discrete code as a one-hot vector -> (H*W, C)
        # Multiply the one-hot row vectors with the embedding matrix will result in another matrix of embeddings,
        # where each row now contains the closest embedding relative to the original pixel vector   
        quantized_x = tf.matmul(one_hot_encoddings, self.embeddings) # (H*W, C)
        quantized_x = tf.reshape(quantized_x, input_shape) # (H, W, C)
        
        #### Add the loss for optimizing the embeddings in the codebook, which contains the commitment loss and the codebook loss
        commitment_loss = tf.reduce_mean((tf.stop_gradient(quantized_x) - x) ** 2)
        codebook_loss = tf.reduce_mean((tf.stop_gradient(x) - quantized_x) ** 2)
        self.add_loss((self.beta * commitment_loss) + codebook_loss)
        # Apply STE for estimating the gradients of the encoding part of the encoder
        quantized_x = x + tf.stop_gradient(quantized_x - x) # Doing this can make the gradient of this whole quantization process become 1
        return quantized_x
    
    def get_closest_codes(self, pixel_vectors):
        '''
            This function finds and returns the indices of the closest embeddings in the codebook for the given pixel vectors
        '''
        # Get the closest embedding via computing L2 distance between itself and the pixel vector
        # Mathematically, it is (x-y)^T(x-y), where x and y are the vectors of C dimensions
        square_pixel_vector_lens = tf.reduce_sum(pixel_vectors ** 2, axis=1, keepdims=True) # (H*W, 1)
        square_embedding_lens = tf.transpose(tf.reduce_sum(self.embeddings ** 2, axis=1, keepdims=True)) # (1, n_embeddings)
        pixel_vec_dot_embedding = tf.matmul(pixel_vectors, self.embeddings, transpose_b=True) # (H*W, C) x (C, n_embeddings) -> (H*W, n_embeddings)
        distances = square_pixel_vector_lens + square_embedding_lens + (2*pixel_vec_dot_embedding) # (H*W, n_embeddings)
        # Get the index of the closest embedding relative to the pixel vector
        quantized_codes = tf.argmin(distances, axis=1) # (H*W, 1)
        return quantized_codes


class ResidualBlock(tfk.Model):
    '''
        This class specifies the component of a residual block, which contains the following layers in order:
        1. A convolutional layer with kernel size = latent_kernel_size, and the output channel is n_latent_channels
        2. Apply Batch Normalization then LeakyReLU
        3. Another convolutional layer with kernel size = 1, and the output channel is n_last_channels
        4. Add the original input to the output produced in 3rd step then apply LeakyReLU
        Note that the shape of the output will be as same as the shape of the input
    '''
    def __init__(self, input_shape, n_latent_channels, n_last_channels, latent_kernel_size, **kwargs):
        super(ResidualBlock, self).__init__(**kwargs)
        self.conv1 = tfk.layers.Conv2D(filters=n_latent_channels, kernel_size=latent_kernel_size, padding='same', input_shape=input_shape[1:])
        self.bn1 = tfk.layers.BatchNormalization()
        self.conv2 = tfk.layers.Conv2D(filters=n_last_channels, kernel_size=1)
    
    def call(self, inputs, training=False):
        x = self.conv1(inputs)
        x = self.bn1(x, training=training)
        x = tf.nn.leaky_relu(x)
        x = self.conv2(x, training=training)
        return tf.nn.leaky_relu(x + inputs)

#TODO
class VQ_VAE(tfk.Model):
    def __init__(self, img_h, img_w, img_c, embedding_dim, n_embeddings, **kwargs):
        super(VQ_VAE, self).__init__(**kwargs)
        self.img_h = img_h # Height of an input image
        self.img_w = img_w # Width of an input image
        self.img_c = img_c # Number of channels of an input image
        self.embedding_dim = embedding_dim
        self.n_embeddings = n_embeddings
        self.encoder = self.create_encoder()
        self.decoder = self.create_decoder()
    
    def create_encoder(self):
        inputs = tfk.Input(shape(self.img_h, self.img_w, self.img_c), name='encoder_input')
        ## First CNN block
        x = tfk.layers.Conv2D(filters=32, kernel_size=3, strides=2, padding='same')(inputs)
        x = tfk.layers.BatchNormalization()(x)
        x = tfk.layers.LeakyReLU()(x)
        ## Second CNN block
        x = tfk.layers.Conv2D(filters=64, kernel_size=3, strides=2, padding='same')(inputs)
        x = tfk.layers.BatchNormalization()(x)
        x = tfk.layers.LeakyReLU()(x)
        #TODO
        return
    def create_decoder(self):
        #TODO
        return

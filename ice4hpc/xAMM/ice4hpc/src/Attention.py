import os
import yaml
import util
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import OneHotEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import Dense, Input, Layer, Dropout ,Reshape
from tensorflow.keras.models import Model
from sklearn.metrics import mean_squared_error,mean_absolute_percentage_error,accuracy_score,confusion_matrix

class CustomLabelEncoder:
    def __init__(self):
        self.label_mapping = {}
    
    def fit(self, labels):
        unique_labels = np.unique(labels)
        self.label_mapping = {label: idx for idx, label in enumerate(unique_labels)}
        self.label_mapping['unknown'] = -1  # Fallback for unseen labels
    
    def transform(self, labels):
        # Convert each label to a hashable type before looking it up
        return [
            self.label_mapping.get(label.item() if isinstance(label, np.ndarray) else label, 
                                   self.label_mapping['unknown'])
            for label in labels
        ]

# Define Attention Layer
class AttentionLayer(Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        self.attention_weights = self.add_weight(
            shape=(input_shape[-1], 1),
            initializer="glorot_uniform",
            trainable=True,
            name="attention_weights",
        )
        self.bias = self.add_weight(
            shape=(1,),
            initializer="zeros",
            trainable=True,
            name="bias",
        )
        super(AttentionLayer, self).build(input_shape)

    def call(self, inputs):
        # Compute attention scores
        scores = tf.matmul(inputs, self.attention_weights) + self.bias
        attention_scores = tf.nn.softmax(scores, axis=1)
        
        # Apply attention scores to inputs
        weighted_inputs = inputs * attention_scores
        return tf.reduce_sum(weighted_inputs, axis=1)  # Reduce along the feature axis

# Create the Model

def create_attention_model(input_dim, num_classes, dropout_rate=0.2):
    inputs = Input(shape=(input_dim,))
    x = Dense(64, activation="relu")(inputs)
    x = Dropout(dropout_rate)(x)
    x = Dense(64, activation="relu")(x)
    x = Reshape((1, 64))(x)  # Use Keras Reshape layer
    attention_output = AttentionLayer()(x)
    x = Dense(32, activation="relu")(attention_output)
    x = Dropout(dropout_rate)(x)
    outputs = Dense(num_classes, activation="softmax")(x)

    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    return model

class Attention():
    def __init__(self, num_of_estimators):
        self.num_of_estimators = int(num_of_estimators)

    def __call__(self, config_yaml, X_train, Y_train, tar_x_scaled, tar_y_scaled):
        with open(config_yaml, "r") as f:
            global_config= yaml.load(f, Loader=yaml.FullLoader)

        label_encoder = OneHotEncoder(sparse_output=False,handle_unknown="ignore")
        label_encoder.fit(Y_train)
        input_dim = X_train.shape[1]
        num_classes = len(np.unique(Y_train))
        # num_classes = len(np.union1d(np.unique(Y_train), np.unique(tar_y_scaled)))

        # Ensure Y_train and tar_y_scaled are correctly encoded as integers
        Y_train_encoded = label_encoder.transform(Y_train)
        tar_y_scaled_encoded=label_encoder.transform(tar_y_scaled)
        # tar_y_scaled_encoded = to_categorical(tar_y_scaled, num_classes=num_classes)

        # print(f"Y_train shape after encoding: {Y_train_encoded.shape}")
        # print(f"tar_y_scaled shape after encoding: {tar_y_scaled_encoded.shape}")

        rp_tree_model = create_attention_model(input_dim, num_classes)
        rp_tree_model.fit(X_train, Y_train_encoded, epochs=20, batch_size=32, validation_split=0.2)

        prediction = rp_tree_model.predict(tar_x_scaled)
        predicted_classes = np.argmax(prediction, axis=1)  # Get predicted classes
        tar_y_scaled_classes = np.argmax(tar_y_scaled_encoded, axis=1)  # Use one-hot encoded labels

        accuracy = accuracy_score(tar_y_scaled_classes, predicted_classes)
        print(f"Accuracy: {accuracy:.2f}")

        conf_matrix = confusion_matrix(tar_y_scaled_classes, predicted_classes)
        print("Confusion Matrix:")
        print(conf_matrix)
        return accuracy
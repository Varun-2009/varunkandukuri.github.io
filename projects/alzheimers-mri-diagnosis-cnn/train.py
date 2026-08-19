import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf


IMAGE_SIZE = (128, 128)
NUM_CLASSES = 4


def synthetic_data(batch_size: int = 16):
    x = np.random.default_rng(42).random((64, *IMAGE_SIZE, 3), dtype=np.float32)
    y = np.arange(64) % NUM_CLASSES
    ds = tf.data.Dataset.from_tensor_slices((x, y)).shuffle(64, seed=42).batch(batch_size)
    return ds.take(3), ds.skip(3)


def directory_data(data_dir: Path, batch_size: int = 16):
    common = dict(image_size=IMAGE_SIZE, batch_size=batch_size, label_mode="int", seed=42)
    train = tf.keras.utils.image_dataset_from_directory(data_dir / "train", shuffle=True, **common)
    val = tf.keras.utils.image_dataset_from_directory(data_dir / "val", shuffle=False, **common)
    return train.prefetch(tf.data.AUTOTUNE), val.prefetch(tf.data.AUTOTUNE)


def build_model(num_classes: int = NUM_CLASSES) -> tf.keras.Model:
    augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.05),
        tf.keras.layers.RandomZoom(0.1),
    ])
    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3))
    x = augmentation(inputs)
    x = tf.keras.layers.Rescaling(1.0 / 255)(x)
    x = tf.keras.layers.Conv2D(24, 3, activation="relu")(x)
    x = tf.keras.layers.MaxPooling2D()(x)
    x = tf.keras.layers.Conv2D(48, 3, activation="relu")(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def main(args):
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    train_ds, val_ds = synthetic_data() if args.synthetic else directory_data(args.data_dir)
    model = build_model()
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(output / "best.keras", save_best_only=True),
        tf.keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True),
    ]
    history = model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks)
    (output / "history.json").write_text(json.dumps(history.history, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--synthetic", action="store_true")
    main(parser.parse_args())


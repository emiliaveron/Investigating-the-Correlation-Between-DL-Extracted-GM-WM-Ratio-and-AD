import os
import shutil
import random
import re

ORIG_DIR = "MRIs_SPLIT_OLD"
OUTPUT_DIR = "MRIs_SPLIT"
IMAGE_DIRS = ["images", "masks"]
TRAIN_RATIO = 0.7
VAL_RATIO = 0.2
TEST_RATIO = 0.1
random.seed(42)

def reorganize_dataset_matched():
    # Collect all image paths
    image_files = []
    mask_files = []
    
    for split in ["train", "val", "test"]:
        img_dir = os.path.join(ORIG_DIR, split, "images")
        msk_dir = os.path.join(ORIG_DIR, split, "masks")
        if not os.path.exists(img_dir):
            continue

        imgs = [f for f in os.listdir(img_dir) if f.endswith((".nii", ".nii.gz"))]
        for img in imgs:
            # Handle double extension .nii.gz
            if img.endswith(".nii.gz"):
                stem = img[:-7]  # remove ".nii.gz"
            else:
                stem = os.path.splitext(img)[0]  # remove ".nii"

            # Construct mask name by adding "_fast_seg.nii.gz"
            mask_name = stem + "_fast_seg.nii.gz"
            mask_candidate = os.path.join(msk_dir, mask_name)

            if os.path.exists(mask_candidate):
                image_files.append(os.path.join(img_dir, img))
                mask_files.append(mask_candidate)
            else:
                raise ValueError(f"Mask not found for image {img}. Expected: {mask_candidate}")

    # Shuffle pairs
    combined = list(zip(image_files, mask_files))
    random.shuffle(combined)
    image_files, mask_files = zip(*combined)

    # Split
    total = len(image_files)
    n_train = int(total * TRAIN_RATIO)
    n_val = int(total * VAL_RATIO)
    n_test = total - n_train - n_val

    splits = {
        "train": (image_files[:n_train], mask_files[:n_train]),
        "val": (image_files[n_train:n_train+n_val], mask_files[n_train:n_train+n_val]),
        "test": (image_files[n_train+n_val:], mask_files[n_train+n_val:])
    }

    # Copy to OUTPUT_DIR
    for split, (imgs, msks) in splits.items():
        for folder in IMAGE_DIRS:
            os.makedirs(os.path.join(OUTPUT_DIR, split, folder), exist_ok=True)
        
        for img, msk in zip(imgs, msks):
            shutil.copy(img, os.path.join(OUTPUT_DIR, split, "images", os.path.basename(img)))
            shutil.copy(msk, os.path.join(OUTPUT_DIR, split, "masks", os.path.basename(msk)))

    print(f"Dataset reorganized: {total} pairs split into train/val/test")

if __name__ == "__main__":
    reorganize_dataset_matched()

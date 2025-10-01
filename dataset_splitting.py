import os
import shutil
import random

def split_mri_dataset_recursive(
    source_root,
    dest_root,
    seed=42,
    dry_run=False
):
    """
    Recursively finds MRI .nii files with *_fast_seg.nii.gz masks,
    and splits them into train/test folders with images/ and masks/.

    Args:
        source_root (str): Root directory of organized patient folders.
        dest_root (str): Destination root containing train/ and test/.
        test_ratio (float): Proportion of data for test split.
        seed (int): Random seed for reproducibility.
        dry_run (bool): If True, prints actions without copying.
    """
    # Step 1: Gather all valid pairs
    file_pairs = []
    for root, _, files in os.walk(source_root):
        for f in files:
            if f.endswith(".nii") and not f.endswith(".nii.gz"):
                base_name = f[:-4]  # remove .nii
                mask_name = f"{base_name}_gm_wm_mask.nii.gz"
                mask_path = os.path.join(root, mask_name)
                img_path = os.path.join(root, f)
                if os.path.exists(mask_path):
                    file_pairs.append((img_path, mask_path))

    # Step 2: Shuffle & split
    random.seed(seed)
    random.shuffle(file_pairs)
    split_idx_train = int(len(file_pairs) * (0.7))
    split_idx_val = int(len(file_pairs) * (0.9))
    train_set = file_pairs[:split_idx_train]
    val_set = file_pairs[split_idx_train:split_idx_val]
    test_set = file_pairs[split_idx_val:]

    # Step 3: Helper to copy files
    def copy_files(pairs, split_name):
        images_dir = os.path.join(dest_root, split_name, "images")
        masks_dir = os.path.join(dest_root, split_name, "masks")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(masks_dir, exist_ok=True)

        for img_file, mask_file in pairs:
            img_dest = os.path.join(images_dir, os.path.basename(img_file))
            mask_dest = os.path.join(masks_dir, os.path.basename(mask_file))
            if dry_run:
                print(f"[{split_name}] Copy image: {img_file} -> {img_dest}")
                print(f"[{split_name}] Copy mask : {mask_file} -> {mask_dest}")
            else:
                shutil.copy2(img_file, img_dest)
                shutil.copy2(mask_file, mask_dest)

    # Step 4: Copy train and test
    copy_files(train_set, "train")
    copy_files(val_set, "val")
    copy_files(test_set, "test")


split_mri_dataset_recursive(
    source_root="MRI_FASTSURFER_IMG_MASK",
    dest_root="MRIs_SPLIT",
)
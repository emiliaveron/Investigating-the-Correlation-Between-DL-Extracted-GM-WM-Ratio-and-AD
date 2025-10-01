import os
import shutil
import re
import glob
from collections import defaultdict
import pandas as pd

# ====== CONFIG ======
orig_dir = "MRIs_IMAGES_FILTERED_NOMASKS"
fastsurfer_dir = "FASTSURFER_MASKS_NII"
out_root = "MRI_FASTSURFER_IMG_MASK"
out_images = os.path.join(out_root, "images")
out_masks  = os.path.join(out_root, "masks")
STRICT_MODE = False   # True -> skip image if aparc OR aseg missing

missing = []
# ====================

os.makedirs(out_images, exist_ok=True)
os.makedirs(out_masks, exist_ok=True)

for fname in sorted(os.listdir(orig_dir)):
    if not (fname.endswith(".nii") or fname.endswith(".nii.gz")):
        continue

    # folder in FastSurfer to use (1st -> subj_base, 2nd -> subj_base_2, ...)
    subj_folder = fname.replace(".nii",'')

    # find aparc/aseg files under FASTSURFER_MASKS_NII/<subj_folder>/mri/
    mri_dir = os.path.join(fastsurfer_dir, subj_folder, "mri")
    aparc_candidates = glob.glob(os.path.join(mri_dir, "aparc*"))
    aseg_candidates  = glob.glob(os.path.join(mri_dir, "aseg*"))

    aparc_src = aparc_candidates[0] if aparc_candidates else None

    # prefer aseg.auto_noCCseg.* if present, else take any aseg*
    aseg_src = None
    for p in aseg_candidates:
        if "noCCseg" in os.path.basename(p):
            aseg_src = p
            break
    if aseg_src is None and aseg_candidates:
        aseg_src = aseg_candidates[0]

    # destination filenames (preserve full original name)
    dest_img = os.path.join(out_images, fname)

    # base without extension
    if fname.endswith(".nii.gz"):
        base_noext = fname[:-7]
    elif fname.endswith(".nii"):
        base_noext = fname[:-4]
    else:
        base_noext = os.path.splitext(fname)[0]

    dest_aparc = os.path.join(out_masks, f"{base_noext}_aparc.nii.gz")
    dest_aseg  = os.path.join(out_masks, f"{base_noext}_aseg.nii.gz")

    # If strict mode, skip if either mask missing
    if STRICT_MODE and (aparc_src is None or aseg_src is None):
        print(f"⚠️ Skipping {fname} because missing mask(s) for {subj_folder} "
              f"(aparc: {'yes' if aparc_src else 'NO'}, aseg: {'yes' if aseg_src else 'NO'})")
        continue

    # copy original image (always, unless we skipped above)
    shutil.copy2(os.path.join(orig_dir, fname), dest_img)

    # copy masks if they exist; if not, log
    if aparc_src:
        shutil.copy2(aparc_src, dest_aparc)
    else:
        print(f"⚠️ Missing aparc for {subj_folder} (image: {fname})")
        missing.append(subj_folder)


    if aseg_src:
        shutil.copy2(aseg_src, dest_aseg)
    else:
        print(f"⚠️ Missing aseg for {subj_folder} (image: {fname})")

print("✅ Finished. Images ->", out_images, "Masks ->", out_masks)

mis = pd.DataFrame(missing, columns=['id'])
mis.to_csv('missing_fastsurfer_masks.csv', index=False)
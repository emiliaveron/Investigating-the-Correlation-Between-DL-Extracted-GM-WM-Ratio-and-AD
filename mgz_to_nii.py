import os
import nibabel as nib

# 📂 Set your input and output directories
input_dir = "FASTSURFER_MASKS"
output_dir = "FASTSURFER_MASKS_NII"

# 🔄 Walk through all subdirectories
for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith(".mgz"):
            input_path = os.path.join(root, file)

            # keep relative subfolder structure
            rel_path = os.path.relpath(root, input_dir)
            save_dir = os.path.join(output_dir, rel_path)
            os.makedirs(save_dir, exist_ok=True)

            output_path = os.path.join(save_dir, file.replace(".mgz", ".nii.gz"))

            print(f"Converting: {input_path} -> {output_path}")
            img = nib.load(input_path)
            nib.save(img, output_path)

print("✅ Conversion complete!")

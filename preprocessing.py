import os
import subprocess

# Set root directory
ROOT_DIR = "adni_data"  # ← change this to your actual ADNI path

def is_nifti(file):
    return file.endswith(".nii") or file.endswith(".nii.gz")

# Walk through all folders
for root, dirs, files in os.walk(ROOT_DIR):
    nifti_files = [f for f in files if is_nifti(f)]
    for f in nifti_files:
        full_path = os.path.join(root, f)
        base = f.replace(".nii.gz", "").replace(".nii", "")
        
        print(f"🔍 Processing: {full_path}")

        brain_prefix = os.path.join(root, f"{base}_brain")
        brain_img = brain_prefix + ".nii.gz"
        fast_prefix = os.path.join(root, f"{base}_fast")

        # Skip if already processed
        if os.path.exists(fast_prefix + "_seg.nii.gz"):
            print(f"🔁 Skipping (already processed): {base}")
            continue

        try:
            # Run BET
            subprocess.run(["bet", full_path, brain_prefix, "-f", "0.5", "-g", "0", "-m"], check=True)

            # Run FAST
            subprocess.run(["fast", "-o", fast_prefix, brain_img], check=True)

            print(f"✅ Saved in: {root}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Error processing {base}: {e}")


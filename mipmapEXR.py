import subprocess
from pathlib import Path
import shutil
import re

def convert_to_mipmap_exr(top_folder: str, recursive: bool = True, sameName: bool = False):
    """
    Converts .exr files to mipmapped .exr using maketx.
    
    Parameters:
    - top_folder (str): Folder containing .exr files.
    - recursive (bool): Whether to recurse into subfolders.
    - sameName (bool): If True, copy original to ./source/, then overwrite with mipmapped version.
    """
    MAKETX_CMD = "maketx"
    top_path = Path(top_folder)

    if not top_path.exists():
        print(f"❌ Folder does not exist: {top_folder}")
        return

    exr_files = list(top_path.rglob("*.exr") if recursive else top_path.glob("*.exr"))
    total_files = len(exr_files)

    print(f"🔍 Found {total_files} .exr files in '{top_folder}' (recursive={recursive})")

    files_to_convert = []

    for exr_file in exr_files:
        name = exr_file.name

        if sameName:
            # Check if backup exists — that means it's already processed
            source_dir = exr_file.parent / "source"
            backup_path = source_dir / exr_file.name
            if backup_path.exists():
                print(f"✅ Skipping (already backed up & mipmapped): {exr_file.relative_to(top_path)}")
                continue
            output_file = exr_file  # same name, same location
        else:
            udim_match = re.match(r"^(.*?)([._])(\d{4})\.exr$", name, re.IGNORECASE)
            if udim_match:
                base, sep, udim = udim_match.groups()
                new_name = f"{base}_mipmap{sep}{udim}.exr"
            else:
                new_name = exr_file.stem + "_mipmap.exr"
            output_file = exr_file.with_name(new_name)
            if output_file.exists():
                print(f"✅ Skipping (already exists): {output_file.relative_to(top_path)}")
                continue

        files_to_convert.append((exr_file, output_file))

    total_to_convert = len(files_to_convert)

    for idx, (exr_file, output_file) in enumerate(files_to_convert, 1):
        print(f"🚀 [{idx}/{total_to_convert}] Converting: {exr_file.relative_to(top_path)}")

        if sameName:
            source_dir = exr_file.parent / "source"
            source_dir.mkdir(exist_ok=True)
            backup_path = source_dir / exr_file.name
            temp_path = exr_file.with_name(exr_file.stem + "_temp.exr")

            # Step 1: backup original
            shutil.copy2(exr_file, backup_path)

            # Step 2: rename original → temp
            exr_file.rename(temp_path)

            # Step 3: maketx → original name
            command = [
                MAKETX_CMD,
                "--prman",
                "--resize",
                "--wrap", "periodic",
                "-o", str(exr_file),  # write to original name
                str(temp_path)
            ]

            try:
                subprocess.run(command, check=True)
                temp_path.unlink()  # remove the temp file after success
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed: {exr_file.name} — {e}")
                # If failed, restore original
                shutil.move(str(backup_path), str(exr_file))
        else:
            command = [
                MAKETX_CMD,
                "--prman",
                "--resize",
                "--wrap", "periodic",
                "-o", str(output_file),
                str(exr_file)
            ]

            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed: {exr_file.name} — {e}")
#---------------------------------------------------------

convert_to_mipmap_exr("/my/Path/here/", True, True)

from flask import current_app
import os


def delete_img(filepath: str, custom_dir='resources'):
    """Delete an image from the filesystem if it exists."""
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    # Extract the filename from the file path
    filename = filepath.rpartition('/')[-1]
    # Generate an absolute path to the image
    img_path = os.path.join(upload_folder, custom_dir, filename)

    if os.path.exists(img_path):
        os.remove(img_path)
        return True
    return False

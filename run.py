import shutil
import os
import subprocess

stakater_theme_source_dir='custom_theme'
overriden_theme_source_dir='overriden_theme'
compiled_theme_dir = 'dist/_theme'

def copy_submodule():
    # Copy the submodule to a specific directory
    source_dir = stakater_theme_source_dir
    destination_dir = compiled_theme_dir
    if os.path.exists(destination_dir):
        shutil.rmtree(destination_dir)
    shutil.copytree(source_dir, destination_dir)
    print("Submodule copied to destination.")

def override_resources():
    # Override resources from another directory
    source_override_dir = overriden_theme_source_dir
    destination_override_dir = compiled_theme_dir
    for item in os.listdir(source_override_dir):
        s = os.path.join(source_override_dir, item)
        d = os.path.join(destination_override_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    print("Resources overridden.")

def mkdocs_serve():
    # Serve the MkDocs site
    subprocess.run(['mkdocs', 'serve'])

if __name__ == "__main__":
    copy_submodule()
    override_resources()
    mkdocs_serve()

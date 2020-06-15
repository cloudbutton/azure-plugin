import cloudbutton.engine.backends as cb_backends
import os
import shutil


storage_backends_dir = os.path.dirname(os.path.abspath(cb_backends.storage.__file__))
compute_backends_dir = os.path.dirname(os.path.abspath(cb_backends.compute.__file__))
dst_storage_backend_path = os.path.join(storage_backends_dir, 'azure_blob')
dst_compute_backend_path = os.path.join(compute_backends_dir, 'azure_fa')

if os.path.isdir(dst_storage_backend_path):
    shutil.rmtree(dst_storage_backend_path)
elif os.path.isfile(dst_storage_backend_path):
    os.remove(dst_storage_backend_path)

if os.path.isdir(dst_compute_backend_path):
    shutil.rmtree(dst_compute_backend_path)
elif os.path.isfile(dst_compute_backend_path):
    os.remove(dst_compute_backend_path)

current_location = os.path.dirname(os.path.abspath(__file__))
src_storage_backend_path = os.path.join(current_location, 'azure_blob')
src_compute_backend_path = os.path.join(current_location, 'azure_fa')

shutil.copytree(src_storage_backend_path, dst_storage_backend_path)
shutil.copytree(src_compute_backend_path, dst_compute_backend_path)

import pywren_ibm_cloud
import os
import shutil

module_location = os.path.dirname(os.path.abspath(pywren_ibm_cloud.__file__))
dst_storage_backend_path = os.path.join(module_location, 'storage', 'backends', 'azure_blob')
dst_compute_backend_path = os.path.join(module_location, 'compute', 'backends', 'azure_fa')
dst_libs_path = os.path.join(module_location, 'libs', 'azure')


if os.path.isdir(dst_storage_backend_path):
    shutil.rmtree(dst_storage_backend_path)
elif os.path.isfile(dst_storage_backend_path):
    os.remove(dst_storage_backend_path)

if os.path.isdir(dst_compute_backend_path):
    shutil.rmtree(dst_compute_backend_path)
elif os.path.isfile(dst_compute_backend_path):
    os.remove(dst_compute_backend_path)

if os.path.isdir(dst_libs_path):
    shutil.rmtree(dst_libs_path)
elif os.path.isfile(dst_libs_path):
    os.remove(dst_libs_path)

current_location = os.path.dirname(os.path.abspath(__file__))
src_storage_backend_path = os.path.join(current_location, 'storage', 'backends', 'azure_blob')
src_compute_backend_path = os.path.join(current_location, 'compute', 'backends', 'azure_fa')
src_libs_path = os.path.join(current_location, 'libs', 'azure')

shutil.copytree(src_storage_backend_path, dst_storage_backend_path)
shutil.copytree(src_compute_backend_path, dst_compute_backend_path)
shutil.copytree(src_libs_path, dst_libs_path)
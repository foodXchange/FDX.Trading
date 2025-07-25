import shutil
import os
import zipfile

# Remove old zip if exists
if os.path.exists('app.zip'):
    os.remove('app.zip')

# Zip the 'app' folder
shutil.make_archive('app', 'zip', root_dir='.', base_dir='app')

# Add requirements.txt and startup.txt to the zip
with zipfile.ZipFile('app.zip', 'a') as zf:
    zf.write('requirements.txt')
    zf.write('startup.txt')
    if os.path.exists('alembic.ini'):
        zf.write('alembic.ini')
    if os.path.exists('migrations'):
        for root, dirs, files in os.walk('migrations'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = file_path.replace('\\', '/').replace('migrations', 'app/migrations', 1)
                zf.write(file_path, arcname=arcname)
print('✅ app.zip created for Azure deployment.') 
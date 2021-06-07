# Install an application that has been uploaded
import os, tarfile, shutil
from modules.switch import switch
def install(path):
    print("Install file", path )
    #File is located in /database/tmp

    # Step 1: Convert .tree file to .tar.xz
    os.rename('database/tmp/{}'.format(path), 'database/tmp/{}'.format(path[:-4] +'tar.xz'))
    # step 2: extract it into .tmp folder
    path = 'database/tmp/{}'.format(path[:-4] +'tar.xz')
    app_name = path[:-7].split('/')[-1]
    print(app_name, path)

    with tarfile.open(path) as f:
        f.extractall('.')



    #Now we have a folder in our root directory.
    # It has three subdirectories.
    # python, template, webstatic,
    # /python/ has to be moved to /programs/{app name}/
    source = '{}/python'.format(app_name)
    dest = 'programs/{}'.format(app_name)
    shutil.move(source, dest)

    # /template/ has to be moved to /app/template/{app name}/
    source = '{}/template'.format(app_name)
    dest = 'app/templates/{}'.format(app_name)
    shutil.move(source, dest)

    # The PNG favicon also needs to be moved to /app/static/appstatic/icon
    shutil.move('{}/{}.png'.format(app_name, app_name), 'app/static/appstatic/icon/{}.png'.format(app_name))

    # Finally, remove the temporary file and installed folder.
    os.remove('database/tmp/{}.tar.xz'.format(app_name))
    shutil.rmtree('{}'.format(app_name))


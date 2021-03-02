# Uninstall a previously installed application
import os
import shutil
def uninstall(target):
    err_msg = ''
    try:
        ##
        print("removing {} from /programs/".format(target))
        shutil.rmtree('programs/{}'.format(target))
    except Exception as e:
        err_msg += 'error removing programs file: {}\n'.format(e)
    try:
        print("removing {} from system icons".format(target))
        os.remove('app/static/appstatic/icon/{}.png'.format(target))
    except Exception as e:
        err_msg += 'error removing app icon: {}\n'.format(e)
    try:
        print("removing {} from system templates")
        shutil.rmtree('app/templates/{}/'.format(target))
    except Exception as e:
        err_msg += 'error removing templates:{}\n'.format(e)

    if err_msg == '':
        print("No errors. ")
    else:
        print(err_msg)
from app import app
from flask import render_template, request
import wget, json, base64, os
from tools.install import install
from tools.misc import default_app
from tools.misc import list_apps
store_ip = 'treecamera.xyz:8001'

categories = {
              1: 'Home and Kitchen',
              2: 'Security',
              3: 'Business',
              4: 'Gaming and Entertainment',
              5: 'Lifestyle and Productivity'
              }


def write_b64_to_file(path, b64):
    data = bytearray(base64.b64decode(b64))
    with open(path, 'w+b') as file:
        file.write(data)


@app.route('/storefront_load_category')
def return_category():
    cat_id = request.args.get('cat_id', default='0', type=int)
    return render_template('store_container.html', store_ip = store_ip, content_path = '/storefront_load_category?cat_id={}'.format(cat_id))

@app.route('/store')
def store_entry():
    return render_template('store_container.html', store_ip = store_ip, content_path = '')

@app.route('/post_download_request')
def download():
    id = request.args.get('id', default='0', type=int)
    filename = wget.download('http://{}/query?id={}'.format(store_ip, id))
    # Json with two parts: meta and base64 tar.xz file.
    with open(filename) as f:
        struc = json.load(f)
    meta = struc['meta']
    program = struc['program']
    write_b64_to_file('database/tmp/{}.tree'.format(meta['name']), program)
    os.remove(filename)
    install('{}.tree'.format(meta['name']))


    return render_template('config.html', list_apps = list_apps(), current_app = default_app(), up_to_date = True)


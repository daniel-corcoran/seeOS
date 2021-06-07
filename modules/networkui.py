## Network management UI
# Provides modules for wi-fi setup
from app import app
from flask import render_template, request
import os
from modules.misc import list_apps
from modules.kiwilog import kiwi
from subprocess import PIPE, Popen
from modules.update import check_update_api
import json

log = kiwi.instance('modules.networkui')

with open('database/see.json') as f:
    see_config = json.load(f)

default_app = see_config['default_app']


def get_nets():

    string = os.popen('nmcli -t -m multiline dev wifi').read()
    schema = []
    net_list = []
    for row in string.split('\n'):

        data = row.split(':')
        if data[0] not in schema and data[0] != '':
            schema.append(data[0])
    net = {}
    for row in string.split('\n'):
        data = row.split(':')

        if data[0] == 'IN-USE':
            if len(net) == len(schema):
                net_list.append(net)
            net = {data[0]: bool(data[1] == '*')}

        else:
            net[data[0]] = data[1:]


    net_list_non_redundant = {}
    net_dic = dict()
    for i, net in enumerate(net_list):
        if net['SSID'][0] in net_list_non_redundant:
            # if it's an active connection, we need to add the active flag to the pre-existing dic!.
            # This is fucked!
            reverse_lookup_key = net_list_non_redundant[net['SSID'][0]]
            if net['IN-USE']:
                net_dic[reverse_lookup_key]['in-use'] = True

            # Skip this since the SSID is already in our net dic

        elif net['SSID'][0] == '':
            ...
        else:
            net_list_non_redundant[net['SSID'][0]] = i
            net_dic[i] = {'in-use': net['IN-USE'],
                                    'rate': net['RATE'][0],
                                    'security': net['SECURITY'][0],
                                    'bars': {'▂___': 1, '▂▄__': 2, '▂▄▆_': 3, '▂▄▆█': 4, '____': 0,
                                             '': 0, '*': 1, '**': 2, "***": 3, '****': 4}[net['BARS'][0].replace(' ', '')],
                                    'ssid': net['SSID'][0],
                                    'secured': bool('WPA' in net['SECURITY'][0])}

    return net_dic


@app.route('/netui_connect', methods=['POST', 'GET'])
def connect():
    ssid = request.form['ssid']
    if 'pwd' in request.form:
        password = request.form['pwd']
    else:
        password = ''
    log.add_log(f'/Wants to connect to SSID {ssid} with password {password}.')
    command = f'nmcli device wifi connect "{ssid}" password {password}'
    output = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = output.communicate()
    log.add_debug(f'stdout: {stdout}')
    log.add_debug(f'stderr: {stderr}')

    # Try to connect to the SSID

    if 'Error' in str(stdout):
        # Error handling.
        log.add_exception(
            f'/sys_ajax_net_connect_wpa could not connect to {ssid} with password {password}. stderr: {stderr}')
        msg = f"Couldn't connect to wi-fi network {ssid}"
    else:
        log.add_log(f'/sys_ajax_net_connect_wpa connected to {ssid} with password {password}. stdout: {stdout}')
        msg=''
    net_dic = get_nets()
    x = list_apps()
    html = render_template('network.html', net_dic = net_dic, msg=msg)
    return render_template('config.html', netui = html, list_apps = x, current_app = default_app, netui_dir = 'config', msg=msg, update=check_update_api())


@app.route('/netui_disconnect', methods=['POST', 'GET'])
def disconnect():
    # Disconnect from a wifi network in the post request.
    ssid = request.form['ssid']
    print("Disconnecting from ", ssid)
    command = f'nmcli connection delete id {ssid}'
    output = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = output.communicate()
    log.add_debug(f'stdout: {stdout}')
    log.add_debug(f'stderr: {stderr}')

    net_dic = get_nets()
    x = list_apps()
    html = render_template('network.html', net_dic=net_dic)
    return render_template('config.html', netui=html, list_apps=x, current_app=default_app, netui_dir='config', update=check_update_api())


@app.route('/netui')
def networkUI():
    net_dic = get_nets()


    x = list_apps()
    html = render_template('network.html', net_dic = net_dic)
    return render_template('config.html', netui = html, list_apps = x, current_app = default_app, netui_dir = 'config', update=check_update_api())


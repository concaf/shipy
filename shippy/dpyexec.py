from docker import Client
import parser
from random import randint

def dpy_stitch(args):
    sane_input = {}

    # remove unnecessary parameters from the args dictionary
    for param, value in args.items():
        if param != 'mode' and param != args['mode'] and value != None:
            sane_input.update({param: value})

    # add tag to the image name if not provided by the user
    if len(sane_input['image'].split(':')) == 1:
        sane_input.update({'image': '{}:latest'.format(sane_input['image'])})

    return sane_input


def dpy_run(client, sane_input):
    if not client.images(name=sane_input['image']):
        client.pull(sane_input['image'])
    if 'name' not in sane_input.keys():
        sane_input.update({'name': 'shippy_{}'.format(randint(1, 999999999))})
    client.create_container(**sane_input)
    client.start(sane_input['name'])


def dpy(args):
    server_url = 'unix://var/run/docker.sock'
    shippy_parser = parser.define_parsers()
    sh_args = shippy_parser.parse_args(args)
    docker_client = Client(base_url=server_url)
    sane_input = dpy_stitch(vars(sh_args))

    if sh_args.mode == 'run':
        dpy_run(docker_client, sane_input)
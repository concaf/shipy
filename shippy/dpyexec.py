from ast import literal_eval
from docker import Client
import logging
import parser
from random import randint
import sys


def dpy_stitch(args):
    sane_input = {}

    # remove unnecessary parameters from the args dictionary
    for param, value in args.items():
        if param not in ('mode', args['mode'], 'isverbose') and value != None:
            sane_input.update({param: value})

    # add tag to the image name if not provided by the user
    if len(sane_input['image'].split(':')) == 1:
        logging.debug('No tag provided, adding tag latest')
        sane_input.update({'image': '{}:latest'.format(sane_input['image'])})

    return sane_input


def dpy_run(client, sane_input):
    if not client.images(name=sane_input['image']):
        logging.info("Container image does not exist locally, pulling now.")
        for pull_output in client.pull(sane_input['image'], stream=True):
            logging.debug(literal_eval(pull_output)['status'])

    if 'name' not in sane_input.keys():
        sane_input.update({'name': 'shippy_{}'.format(randint(1, 999999999))})

    logging.debug("Creating container now.")
    client.create_container(**sane_input)

    logging.info("Running container now.")
    client.start(sane_input['name'])


def dpy(args):
    shippy_parser = parser.define_parsers()
    sh_args = shippy_parser.parse_args(args)

    # set logging level
    if sh_args.isverbose:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.debug("Setting logging level to logging.DEBUG")
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    server_url = 'unix://var/run/docker.sock'

    docker_client = Client(base_url=server_url)

    sane_input = dpy_stitch(vars(sh_args))

    if sh_args.mode == 'run':
        dpy_run(docker_client, sane_input)

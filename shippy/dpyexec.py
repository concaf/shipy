from docker import Client
import parser


def dpy_stitch(args):
    sane_input = {}
    for param, value in args.items():
        if param == 'mode' or param == args['mode'] or value == None:
            pass
        else:
            sane_input.update({param: value})
    return sane_input


def dpy_exec(client, mode, input):
    if mode == 'run':
        client.create_container(**input)
        client.start(input['name'])


def dpy(args):
    server_url = 'unix://var/run/docker.sock'
    shippy_parser = parser.define_parsers()
    sh_args = shippy_parser.parse_args(args)
    docker_client = Client(base_url=server_url)
    sane_input = dpy_stitch(vars(sh_args))
    dpy_exec(docker_client, sh_args.mode, sane_input)
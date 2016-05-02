from ast import literal_eval
from copy import deepcopy
from docker import Client, errors
import logging
import parser
import sys


class Shipy(object):
    def stitch(self, args):
        sane_input = {}

        # remove unnecessary parameters from the args dictionary
        for param, value in args.items():
            if param not in ('mode', args['mode'], 'isverbose') and \
                    value is not None:
                sane_input.update({param: value})

        return sane_input

    def run(self, client, sane_input):
        sane_create = deepcopy(sane_input)
        sane_start = {}
        host_config_params = {}

        # add tag to the image name if not provided by the user
        if len(sane_input['image'].split(':')) == 1:
            logging.debug('No tag provided, pulling tag latest')
            sane_create.update({'image': '{}:latest'.format(sane_input['image'])})

        # pull image if it does not exist
        if not client.images(name=sane_input['image']):
            logging.info('Container image does not exist locally, pulling ...')
            for pull_output in client.pull(sane_input['image'], stream=True):
                logging.debug(literal_eval(pull_output)['status'])

        # parse volume bindings
        if 'volumes' in sane_input.keys():
            volume_bindings_list = sane_input['volumes'].split(':')

            # does not matter if only host or both host and guest bindings are
            # specified, this is just exposing the specified volume
            if len(volume_bindings_list) in (1, 2):
                sane_create.update({'volumes': volume_bindings_list[0]})
            if len(volume_bindings_list) == 2:
                logging.debug('Passing volume bindings to the host_config')
                host_config_params.update({'binds': [sane_input['volumes']]})

        # pass host_config or not
        if len(host_config_params) > 0:
            logging.debug('Creating host_config.')
            sane_create.update({'host_config':
                                client.create_host_config(**host_config_params)})

        logging.debug('Creating container.')
        container_info = client.create_container(**sane_create)
        sane_start.update({'container': container_info['Id']})
        logging.info('Running container {}.'.format(container_info['Id']))
        client.start(**sane_start)

    def ps(self, client, sane_input):

        ps_output = client.containers(**sane_input)
        for container in ps_output:
            logging.info('Name: {}, ID: {}, State: {}'.format(
                container['Names'][0].split('/')[1],
                container['Id'][:8],
                container['State']
                )
            )

        return ps_output

    def kill(self, client, sane_input):

        try:
            client.kill(**sane_input)
            logging.info('Killed container {}'.format(sane_input['container']))
            return True
        except errors.NotFound:
            logging.info('Container {} not found.'.format(sane_input['container']))
            return False

    def stop(self, client, sane_input):

        try:
            client.stop(**sane_input)
            logging.info('Stopped container {}'.format(sane_input['container']))
            return True
        except errors.NotFound:
            logging.info('Container {} not found.'.format(sane_input['container']))
            return False

    def rm(self, client, sane_input):

        try:
            client.remove_container(**sane_input)
            logging.info('Removed container {}'.format(sane_input['container']))
        except errors.NotFound:
            logging.info('Container {} not found.'.format(sane_input['container']))
        except Exception as e:
            logging.info(e.message)

    def pull(self, client, sane_input):

        # add tag to the image name if not provided by the user
        if len(sane_input['repository'].split(':')) == 1:
            logging.info('No tag provided, pulling tag latest')
            sane_input.update({'repository': '{}:latest'.format(
                sane_input['repository'])})

        try:
            for pull_output in client.pull(sane_input['repository'], stream=True):
                logging.debug(literal_eval(pull_output)['status'])
            logging.info('Pulled image {}'.format(sane_input['repository']))

        except:
            logging.info('Could not pull image {}'.format(
                sane_input['repository']))

    def restart(self, client, sane_input):

        try:
            client.restart(**sane_input)
            logging.info('Restarted container {}'.format(sane_input['container']))

        except errors.NotFound:
            logging.info('Could not find container {}'.format(
                sane_input['container']))

    def dpy(self, args):

        if '--file' in args:
            f_pos = args.index('--file')

            with open(args[f_pos+1]) as f:
                command = f.readline().split()

                if command[0] == 'docker':
                    args = command[1:]
                else:
                    raise SyntaxError(
                        'The input file has a malformed docker command.')

        shipy_parser = parser.define_parsers()
        sh_args = shipy_parser.parse_args(args)

        # set logging level
        if sh_args.isverbose:
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            logging.debug('Setting logging level to logging.DEBUG')
        else:
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)

        server_url = 'unix://var/run/docker.sock'

        docker_client = Client(base_url=server_url)

        sane_input = self.stitch(vars(sh_args))

        if sh_args.mode == 'run':
            self.run(docker_client, sane_input)

        if sh_args.mode == 'ps':
            self.ps(docker_client, sane_input)

        if sh_args.mode == 'kill':
            self.kill(docker_client, sane_input)

        if sh_args.mode == 'stop':
            self.stop(docker_client, sane_input)

        if sh_args.mode == 'rm':
            self.rm(docker_client, sane_input)

        if sh_args.mode == 'pull':
            self.pull(docker_client, sane_input)

        if sh_args.mode == 'restart':
            self.restart(docker_client, sane_input)

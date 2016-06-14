from ast import literal_eval
from docker import Client, errors
import logging
import parser
import sys


class Shipy(object):
    def _sanify(self, args):
        sane_input = {}

        # remove unnecessary parameters from the args dictionary
        for param, value in args.items():
            if param not in ('mode', args['mode'], 'isverbose') and \
                    value not in (None, False):
                sane_input.update({param: value})

            if param == 'labels' and value is not None:
                label_dict = {}
                for label in value:
                    k, v = label.split('=')
                    label_dict.update({k: v})
                sane_input.update({param: label_dict})
        return sane_input

    def _host_config_gen(self, client, args):
        host_config_params = {}
        parameters = [
            'binds',
            'port_bindings',
            # 'lxc_conf', # not implemented
            'oom_kill_disable',
            'oom_score_adj',
            'publish_all_ports',
            'links',
            'privileged',
            'dns',
            'dns_search',
            'volumes_from',
            'network_mode',
            'restart_policy',
            'cap_add',
            'cap_drop',
            'extra_hosts',
            'read_only',
            'pid_mode',
            'ipc_mode',
            'security_opt',
            'ulimits',
            'log_config',
            'mem_limit',
            'memswap_limit',
            'mem_swappiness',
            'shm_size',
            # 'cpu_group', # not implemented
            'cpu_period',
            'group_add',
            'devices',
            'tmpfs'
        ]

        for param in parameters:
            if param in args.keys():
                # Check if the parameter value is False
                if args[param] and param != 'port_bindings':
                    host_config_params.update({param: args[param]})
                    del args[param]

                if param == 'port_bindings':
                    create_container_bindings = []
                    host_config_bindings = {param: {}}
                    # setting container port
                    for bindings in args[param]:
                        ports = bindings.split(':')
                        container_port = ports[-1]
                        host_params = ports[:-1]

                        if len(host_params) == 0:
                            host_bindings = None
                        elif len(host_params) == 1:
                            host_bindings = ports[:-1]
                        elif len(host_params) == 2:
                            host_bindings = tuple(ports[:-1])
                        else:
                            raise Exception

                        # add /tcp as default for container port
                        if container_port[-3:] not in ('tcp', 'udp'):
                            container_port = '{}/tcp'.format(container_port)
                        protocol = container_port[-3:]
                        only_port = container_port[:-4]
                        # append to create_container bindings
                        create_container_bindings.append((only_port, protocol))

                        # host_config port bindings
                        host_config_bindings[param].update(
                            {container_port: host_bindings})

                    # pass create_container bindings
                    args['ports'] = create_container_bindings

                    # pass host_config bindinds
                    host_config_params[param] = host_config_bindings[param]

                    del args[param]

                if param == 'binds':
                    volume_bindings = []
                    for bindings in host_config_params[param]:
                        volume_bindings.append(bindings.split(':')[0])
                    args.update({'volumes': volume_bindings})

                if param == 'links':
                    final_links = []
                    links = host_config_params[param]

                    for link in links:
                        link_split = link.split(':')

                        if len(link_split) == 1:
                            final_links.append((link_split[0], link_split[0]))
                        else:
                            final_links.append((link_split[0], link_split[1]))

                    host_config_params[param] = final_links

        if len(host_config_params) > 0:
            logging.debug('Creating host_config.')
            host_config = client.create_host_config(**host_config_params)
        else:
            host_config = None
        return args, host_config

    def run(self, client, sane_input):

        # pull image if it does not exist
        if not client.images(name=sane_input['image']):
            logging.info('Container image does not exist locally, pulling ...')
            self.pull(client, sane_input)

        # Create and start the container

        return self.start(client, self.create(client, sane_input))

    def start(self, client, cid):
        sane_start = {}
        sane_start.update({'container': cid})
        try:
            logging.info('Running container {}.'.format(cid))
            client.start(**sane_start)
            return cid
        except Exception as e:
            logging.info(e)
            return False

    def create(self, client, sane_create):
        if len(sane_create['image'].split(':')) == 1:
            logging.debug('No tag provided, using tag latest')
            sane_create.update({'image': '{}:latest'.
                               format(sane_create['image'])})

        sane_create, host_config = self._host_config_gen(client, sane_create)
        if host_config:
            sane_create.update({'host_config': host_config})

        logging.debug('Creating container.')
        container_info = client.create_container(**sane_create)
        return container_info['Id']

    def ps(self, client, sane_input):

        ps_output = client.containers(**sane_input)
        for container in ps_output:
            logging.info('Name: {}, ID: {}'.format(
                container['Names'][0].split('/')[1],
                container['Id'][:8]))

        return ps_output

    def kill(self, client, sane_input):

        try:
            client.kill(**sane_input)
            logging.info('Killed container {}'.format(sane_input['container']))
            return True
        except errors.NotFound:
            logging.info('Container {} not found.'
                         .format(sane_input['container']))
            return False

    def stop(self, client, sane_input):

        try:
            client.stop(**sane_input)
            logging.info('Stopped container {}'
                         .format(sane_input['container']))
            return True
        except errors.NotFound:
            logging.info('Container {} not found.'
                         .format(sane_input['container']))
            return False

    def rm(self, client, sane_input):

        try:
            client.remove_container(**sane_input)
            logging.info('Removed container {}'
                         .format(sane_input['container']))
        except errors.NotFound:
            logging.info('Container {} not found.'
                         .format(sane_input['container']))
        except Exception as e:
            logging.info(e.message)

    def pull(self, client, sane_input):

        # add tag to the image name if not provided by the user
        if len(sane_input['image'].split(':')) == 1:
            logging.info('No tag provided, pulling tag latest')
            sane_input.update({'image': '{}:latest'.format(
                sane_input['image'])})

        try:
            for pull_output in client.pull(sane_input['image'], stream=True):
                logging.debug(literal_eval(pull_output)['status'])

            for images in client.images():
                if images['RepoTags'][0] == sane_input['image']:
                    logging.info('Pulled image {}'.format(
                        sane_input['image']))
                    return True

        except:
            logging.info('Could not pull image {}'.format(
                sane_input['image']))
            return False

    def restart(self, client, sane_input):

        try:
            client.restart(**sane_input)
            logging.info('Restarted container {}'
                         .format(sane_input['container']))

        except errors.NotFound:
            logging.info('Could not find container {}'.format(
                sane_input['container']))

    def shipy(self, args):

        "Check if input is from a file"
        if '--file' in args:
            f_pos = args.index('--file')

            with open(args[f_pos + 1]) as f:
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

        sane_input = self._sanify(vars(sh_args))

        if sh_args.mode == 'run':
            return self.run(docker_client, sane_input)

        if sh_args.mode == 'ps':
            return self.ps(docker_client, sane_input)

        if sh_args.mode == 'kill':
            return self.kill(docker_client, sane_input)

        if sh_args.mode == 'stop':
            return self.stop(docker_client, sane_input)

        if sh_args.mode == 'rm':
            return self.rm(docker_client, sane_input)

        if sh_args.mode == 'pull':
            return self.pull(docker_client, sane_input)

        if sh_args.mode == 'restart':
            return self.restart(docker_client, sane_input)

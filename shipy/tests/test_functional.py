import pytest
from utils import cinput, client, shipy, container_name as cn,\
    test_docker_run_template as run_template

cimage = 'busybox'
cargs = 'ping 127.0.0.1'


def test_input_sanitization(shipy):
    test_input = {'test_mode': True, 'sanitized_input': True,
                  'isverbose': False, 'mode': 'test_mode'}

    assert {'sanitized_input': True} == shipy._sanify(test_input)


def test_malformed_docker_file_input(shipy, tmpdir):
    tmp_path = tmpdir.mkdir('shipy_temp').join('shipy_test')
    tmp_path.write('dckr run {} {}'.format(cimage, cargs))

    args = ['--file', str(tmp_path)]
    with pytest.raises(SyntaxError):
        shipy.shipy(args)


def test_docker_run_basic(client, shipy):
    container = shipy.shipy(
        cinput('run --name {} {} {}'.format(cn(), cimage, cargs)))
    assert 1 == len(client.containers(
        filters={'id': container, 'status': 'running'}))


def test_docker_run_name(client, shipy):
    cn = 'bruce-batman-wayne'
    run_template(client, shipy, cn=cn)

    assert 1 == len(client.containers(filters={'name': cn}))


def test_docker_run_args(client, shipy):
    cargs = 'ping -v -c 100 127.0.0.1'
    container = run_template(client, shipy, cargs=cargs)

    assert cargs == '{} {}'.format(
        client.inspect_container(container)['Path'],
        ' '.join(client.inspect_container(container)['Args']))


def test_docker_run_entrypoint(client, shipy):
    cargs = '-c 100 127.0.0.1'
    farg = '--entrypoint'
    fval = ('ping',)
    container = run_template(client, shipy, farg=farg, fval=fval, cargs=cargs)

    assert fval[0] == \
           client.inspect_container(container)['Config']['Entrypoint'][0]


def test_docker_run_hostname(client, shipy):
    farg = '--hostname'
    fval = ('batman',)
    container = run_template(client, shipy, farg, fval=fval)
    assert fval[0] == \
           client.inspect_container(container)['Config']['Hostname']


def test_docker_run_user(client, shipy):
    argument = ('-u', '--user')
    fval = ('root',)

    for farg in argument:
        container = run_template(client, shipy, farg=farg, fval=fval)
        assert fval[0] == \
               client.inspect_container(container)['Config']['User']


def test_docker_run_env(client, shipy):
    argument = ('-e', '--env')
    fval = ('bat=man', 'bruce=wayne')

    for farg in argument:
        container = run_template(client, shipy,
                                 farg=farg, fval=fval)

        assert list(fval) == \
               client.inspect_container(container)['Config']['Env']


def test_docker_run_cpu_shares(client, shipy):
    farg = '--cpu-shares'
    fval = (5,)
    container = run_template(client, shipy, farg=farg, fval=fval)

    assert fval[0] == \
           client.inspect_container(container)['HostConfig']['CpuShares']


def test_docker_run_workdir(client, shipy):
    argument = ('-w', '--workdir')
    fval = ('/tmp',)
    for farg in argument:
        container = run_template(client, shipy, farg=farg, fval=fval)
        assert fval[0] == \
               client.inspect_container(container)['Config']['WorkingDir']


def test_docker_run_mac_address(client, shipy):
    farg = '--mac-address'
    fval = ('aa:aa:aa:aa:aa:aa',)
    container = run_template(client, shipy, farg=farg, fval=fval)

    assert fval[0] == \
           client.inspect_container(container)['NetworkSettings']['MacAddress']


def test_docker_run_labels(client, shipy):
    argument = ('-l', '--label')
    fval = ('batman=begins', 'thedarkknight=rises')
    for farg in argument:
        container = run_template(client, shipy,
                                 farg=farg, fval=fval)

        for label in fval:
            l = label.split('=')
            assert l[1] == \
                client.inspect_container(container)['Config']['Labels'][l[0]]


def test_docker_run_stop_signal(client, shipy):
    farg = '--stop-signal'
    fval = ('SIGKILL',)
    container = run_template(client, shipy, farg=farg, fval=fval)

    assert fval[0] == \
           client.inspect_container(container)['Config']['StopSignal']


def test_docker_run_volumes(client, shipy):
    argument = ('-v', '--volume')
    fval = ('/test_dir1:/test_dir_mount1:ro', '/test_dir2:/tmp')

    for farg in argument:
        container = run_template(client, shipy,
                                 farg=farg, fval=fval)

        binding_list = []
        for binding in fval:
            if len(binding) > 1:
                binding_list.append(binding)

        assert binding_list == \
               client.inspect_container(container)['HostConfig']['Binds']

        # this is asserting if the volumes are exposed on the container or not
        # a bit different from docker run, but can be called ideal
        assert_dict = {}
        for value in fval:
            assert_dict.update({value.split(':')[0]: {}})

        assert assert_dict == \
               client.inspect_container(container)['Config']['Volumes']


# def test_docker_run_ports(client, shipy):
#     argument = ('-p', '--publish')
#     fval = ('13370:23370/udp', '13371:23371', '13372:127.0.0.1:23372', '13373', )
#     ext_fval = list(fval)
#     for index, value in enumerate(fval):
#         if value[-3:] in ('tcp', 'udp'):
#             pass
#         else:
#             ext_fval[index] = '{}/tcp'.format(value)
#
#     for farg in argument:
#         container = run_template(client, shipy,
#                                  farg=farg, fval=fval)
#
#         assert_dict ={}
#         for value in fval:
#             assert_dict.update({value.split(':')[0]: {}})
#
#         assert assert_dict == \
#                client.inspect_container(container)['Config']['ExposedPorts']
#
#         client.inspect_container(container)['HostConfig']['PortBindings']
#         client.inspect_container(container)['NetworkSettings']['Networks']['Ports']

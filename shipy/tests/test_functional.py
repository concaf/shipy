import pytest
from utils import client, shipy, container_name as cn

cimage = 'busybox'
cargs = 'ping 127.0.0.1'


def cinput(cmd):
    return cmd.split()


def test_input_sanitization(shipy):
    shipy = shipy
    test_input = {'test_mode': True, 'sanitized_input': True,
                  'isverbose': False, 'mode': 'test_mode'}

    assert {'sanitized_input': True} == shipy._sanify(test_input)


def test_malformed_docker_file_input(shipy, tmpdir):
    shipy = shipy
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
    shipy.shipy(
        cinput('run --name {} {} {}'.
               format('bruce-batman-wayne', cimage, cargs)))
    assert 1 == len(client.containers(
        filters={'name': 'bruce-batman-wayne'}))


def test_docker_run_args(client, shipy):
    cargs = 'ping -v -c 100 127.0.0.1'
    container = shipy.shipy(
        cinput('run --name {} {} {}'.format(cn(), cimage, cargs)))
    assert cargs == '{} {}'.format(
        client.inspect_container(container)['Path'],
        ' '.join(client.inspect_container(container)['Args']))


def test_docker_run_entrypoint(client, shipy):
    entrypoint = 'ping'
    cargs = '-c 100 127.0.0.1'
    container = shipy.shipy(
        cinput('run --entrypoint {} --name {} {} {}'
               .format(entrypoint, cn(), cimage, cargs)))
    assert entrypoint == \
        client.inspect_container(container)['Config']['Entrypoint'][0]


def test_docker_run_hostname(client, shipy):
    hostname = 'batman'
    container = shipy.shipy(
        cinput('run --hostname {} --name {} {} {}'
               .format(hostname, cn(), cimage, cargs)))
    assert hostname == \
           client.inspect_container(container)['Config']['Hostname']


def test_docker_run_user(client, shipy):
    user = 'root'
    arg = ('-u', '--user')
    for argument in arg:
        container = shipy.shipy(
            cinput('run {} {} --name {} {} {}'
                   .format(argument, user, cn(), cimage, cargs)))
        assert user == \
               client.inspect_container(container)['Config']['User']


def test_docker_run_env(client, shipy):
    arg = ('-e', '--env')
    env_var1 = 'bat=man'
    env_var2 = 'bruce=wayne'
    for argument in arg:
        container = shipy.shipy(
            cinput('run {} {} {} {} --name {} {} {}'
                   .format(argument, env_var1, argument, env_var2,
                           cn(), cimage, cargs)))
        assert [env_var1, env_var2] == \
               client.inspect_container(container)['Config']['Env']
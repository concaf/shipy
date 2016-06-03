import pytest
from utils import cinput, client, shipy, container_name as cn,\
    test_docker_run_template as run_template

cimage = 'busybox'
cargs = 'ping 127.0.0.1'


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
    fval = 'ping'
    container = run_template(client, shipy, farg=farg, fval=fval, cargs=cargs)

    assert fval == \
           client.inspect_container(container)['Config']['Entrypoint'][0]


def test_docker_run_hostname(client, shipy):
    farg = '--hostname'
    fval = 'batman'
    container = run_template(client, shipy, farg, fval=fval)
    assert fval == \
           client.inspect_container(container)['Config']['Hostname']


def test_docker_run_user(client, shipy):
    argument = ('-u', '--user')
    fval = 'root'

    for farg in argument:
        container = run_template(client, shipy, farg=farg, fval=fval)
        assert fval == \
               client.inspect_container(container)['Config']['User']


def test_docker_run_env(client, shipy):
    argument = ('-e', '--env')
    fval = 'bat=man'
    fval2 = 'bruce=wayne'

    for farg in argument:
        container = run_template(client, shipy,
                                 farg=farg, fval=fval, fval2=fval2)

        assert [fval, fval2] == \
               client.inspect_container(container)['Config']['Env']


def test_docker_run_cpu_shares(client, shipy):
    farg = '--cpu-shares'
    fval = 5
    container = run_template(client, shipy, farg=farg, fval=fval)

    assert fval == \
           client.inspect_container(container)['HostConfig']['CpuShares']


def test_docker_workdir(client, shipy):
    argument = ('-w', '--workdir')
    fval = '/tmp'
    for farg in argument:
        container = run_template(client, shipy, farg=farg, fval=fval)
        assert fval == \
               client.inspect_container(container)['Config']['WorkingDir']
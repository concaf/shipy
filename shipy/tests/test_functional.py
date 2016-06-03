import pytest
from utils import client, shipy, container_name as cn


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
    tmp_path.write('dckr run busybox 8.8.8.8')

    args = ['--file', str(tmp_path)]
    with pytest.raises(SyntaxError):
        shipy.shipy(args)


def test_docker_run_basic(client, shipy):
    container = shipy.shipy(
        cinput('run --name {} busybox ping 127.0.0.1'.format(cn())))
    assert len(client.containers(
        filters={'id': container, 'status': 'running'})) == 1

import docker
import pytest
from random import randint
from shipy.dpyexec import Shipy


@pytest.fixture
def shipy():
    return Shipy()


@pytest.fixture(scope='function')
def client(request):
    client = docker.Client(base_url='unix://var/run/docker.sock')

    def container_fin():
        for container in client.containers(all=True):
            name = str(container['Names'][0])[1:]
            if name.startswith('bruce') and \
                    name.endswith('wayne'):
                client.remove_container(name, force=True)

    request.addfinalizer(container_fin)
    return client


def container_name():
    prefix = 'bruce'
    suffix = 'wayne'
    return '{}-{}-{}'.format(prefix, randint(1, 10000000), suffix)

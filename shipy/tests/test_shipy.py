import pytest
import os
from shipy.dpyexec import dpy_stitch, dpy


def test_input_sanitization():
    test_input = {'test_mode': True, 'sanitized_input': True,
                  'isverbose': False, 'mode': 'test_mode'}

    assert {'sanitized_input': True} == dpy_stitch(test_input)


def test_malformed_docker_file_input():
    tmp_path = '/tmp/shipy_test'
    args = ['--file', tmp_path]

    with open(tmp_path, mode='w') as f:
        f.write('dckr run busybox 8.8.8.8')

    with pytest.raises(SyntaxError):
        dpy(args)

    os.remove(tmp_path)

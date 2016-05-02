import pytest
from shipy.dpyexec import dpy_stitch, dpy


def test_input_sanitization():
    test_input = {'test_mode': True, 'sanitized_input': True,
                  'isverbose': False, 'mode': 'test_mode'}

    assert {'sanitized_input': True} == dpy_stitch(test_input)


def test_malformed_docker_file_input(tmpdir):
    tmp_path = tmpdir.mkdir('shipy_temp').join('shipy_test')
    tmp_path.write('dckr run busybox 8.8.8.8')

    args = ['--file', str(tmp_path)]
    with pytest.raises(SyntaxError):
        dpy(args)

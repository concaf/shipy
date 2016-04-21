import argparse


def define_parsers():
    shipy_parser = argparse.ArgumentParser(prog='shipy')
    shipy_parser.add_argument(
        '-V',
        '--verbose',
        default=False,
        dest='isverbose',
        action='store_true',
        help='shows more verbose output'
    )
    shipy_subparsers = shipy_parser.add_subparsers(dest='mode')
    run_parser(shipy_subparsers)
    ps_parser(shipy_subparsers)
    kill_parser(shipy_subparsers)
    stop_parser(shipy_subparsers)
    rm_parser(shipy_subparsers)
    pull_parser(shipy_subparsers)
    restart_parser(shipy_subparsers)

    return shipy_parser


def run_parser(subparsers):
    run_subparser = subparsers.add_parser('run')
    run_subparser.add_argument(
        'run',
        action='store_true'
    )
    run_subparser.add_argument(
        'image',
        help='the image to run'
    )
    run_subparser.add_argument(
        'command',
        nargs='?',
        help='the command to be run in the container'
    )
    run_subparser.add_argument(
        '--name',
        type=str,
        help='a name for the container'
    )
    run_subparser.add_argument(
        '--entrypoint',
        type=str,
        help='an entrypoint'
    )
    run_subparser.add_argument(
        '-d',
        action='store_true',
        dest='detach',
        help='detached mode, run container in the background'
    )
    run_subparser.add_argument(
        '-v',
        '--volume',
        dest='volumes',
        help='bind mount a volume'
    )


def ps_parser(subparsers):
    ps_subparser = subparsers.add_parser('ps')
    ps_subparser.add_argument(
        'ps',
        action='store_true'
    )
    ps_subparser.add_argument(
        '-a',
        '--all',
        dest='all',
        action='store_true',
        help='show all containers'
    )


def kill_parser(subparsers):
    kill_subparser = subparsers.add_parser('kill')
    kill_subparser.add_argument(
        'kill',
        action='store_true',
        help='kill a container'
    )
    kill_subparser.add_argument(
        'container',
        help='the container to kill'
    )


def stop_parser(subparsers):
    stop_parser = subparsers.add_parser('stop')
    stop_parser.add_argument(
        'stop',
        action='store_true',
        help='stop a running container'
    )
    stop_parser.add_argument(
        'container',
        help='the container to stop'
    )


def rm_parser(subparsers):
    rm_parser = subparsers.add_parser('rm')
    rm_parser.add_argument(
        'rm',
        action='store_true',
        help='remove a container'
    )
    rm_parser.add_argument(
        'container',
        help='the container to remove'
    )
    rm_parser.add_argument(
        '-f',
        '--force',
        dest='force',
        action='store_true',
        help='force the removal of a running container'
    )
    rm_parser.add_argument(
        '-v',
        '--volumes',
        dest='v',
        action='store_true',
        help='remove the volumes associated with the container'
    )
    rm_parser.add_argument(
        '-l',
        '--link',
        dest='link',
        action='store_true',
        help='remove the specified link and not the underlying container'
    )


def pull_parser(subparsers):
    pull_parser = subparsers.add_parser('pull')
    pull_parser.add_argument(
        'pull',
        action='store_true',
        help='pull a container image'
    )
    pull_parser.add_argument(
        'repository',
        help='the container image to pull'
    )


def restart_parser(subparsers):
    restart_parser = subparsers.add_parser('restart')
    restart_parser.add_argument(
        'restart',
        action='store_true',
        help='restart a container'
    )
    restart_parser.add_argument(
        'container',
        help='the container image to pull'
    )

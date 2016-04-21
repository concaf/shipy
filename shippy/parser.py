import argparse


def define_parsers():
    shippy_parser = argparse.ArgumentParser(prog='shippy')
    shippy_parser.add_argument(
        '-V',
        '--verbose',
        default=False,
        dest='isverbose',
        action='store_true',
        help='shows more verbose output'
    )
    shippy_subparsers = shippy_parser.add_subparsers(dest='mode')
    run_parser(shippy_subparsers)
    ps_parser(shippy_subparsers)
    kill_parser(shippy_subparsers)
    stop_parser(shippy_subparsers)
    return shippy_parser


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
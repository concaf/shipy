import argparse

def define_parsers():
    shippy_parser = argparse.ArgumentParser(prog='shippy')
    shippy_parser.add_argument(
        '-v',
        '--verbose',
        default=False,
        dest='isverbose',
        action='store_true',
        help='shows more verbose output'
    )
    shippy_subparsers = shippy_parser.add_subparsers(dest='mode')
    run_parser(shippy_subparsers)
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
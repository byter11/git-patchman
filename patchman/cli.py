import argparse
from patchman import __version__


def main(args=None):
    example_text = '''examples:
    git graph
    git graph -p examples/demo -n btc -f svg
    '''

    parser = argparse.ArgumentParser(
        prog='git patchman',
        description='',
        epilog=example_text,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-V', '--version', action='version',
                        version=__version__)

    subparsers = parser.add_subparsers()

    create = subparsers.add_parser('add')
    create.add_argument('name')
    create.add_argument('--from-commit', type=str, default='HEAD~1',
                        help='commit')
    create.add_argument('--from-changes', type=bool, default=False,
                        help='create patch from current changes')
    create.add_argument('--append', type=bool, default=False,
                        help='append to existing patch')

    delete = subparsers.add_parser('delete')
    delete.add_argument('name')

    apply = subparsers.add_parser('apply')
    apply.add_argument('name')
    apply.add_argument('-R', '--revert', type=bool, default=False,
                       help='revert the patch')

    args = parser.parse_args(args=args)
    print(args)


if __name__ == "__main__":
    main()

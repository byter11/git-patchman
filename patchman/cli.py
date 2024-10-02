import argparse
from patchman import __version__
from patchman.manager import PatchManager
from patchman.tui import PatchTUI


def create_parser():
    """
    Create an argument parser for the patch management commands.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Manage Git patches with commands to add, delete, "
        "and apply patches."
    )

    parser.add_argument('-V', '--version', action='version',
                        version=__version__)

    subparsers = parser.add_subparsers(dest="command", required=True,
                                       help="Available commands")

    # 'add' command
    add_parser = subparsers.add_parser("add", help="Add a patch")
    add_parser.add_argument(
        "name", type=str, help="Name of the patch")
    add_parser.add_argument("commit", nargs="?", default="",
                            help="Git commit identifier (optional)")
    add_parser.add_argument(
        "--from-changes",
        action="store_true",
        help="Use uncommitted changes instead of a commit"
    )

    # 'delete' command
    delete_parser = subparsers.add_parser("delete", help="Delete a patch")
    delete_parser.add_argument("name", nargs='?', default='', type=str,
                               help="Name of the patch to delete")

    # 'apply' command
    apply_parser = subparsers.add_parser(
        "apply", help="Apply or revert a patch")
    apply_parser.add_argument("name", nargs='?', default='', type=str,
                              help="Name of the patch to apply or revert")
    apply_parser.add_argument(
        "-R", "--reverse", action="store_true",
        help="Revert the patch instead of applying it"
    )

    show_parser = subparsers.add_parser("show", help="View a patch diff")
    show_parser.add_argument("name", nargs='?', default='', type=str,
                             help="Name of the patch to show")

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    manager = PatchManager()
    tui = PatchTUI()
    # test

    if args.command == "add":
        manager.add(args.name, args.commit, args.from_changes)
    elif args.command == "delete":
        if not args.name:
            args.name = tui.select_patch(manager.list())
        manager.delete(args.name)
    elif args.command == "apply":
        if not args.name:
            args.name = tui.select_patch(manager.list())
        manager.apply(args.name, args.reverse)
    elif args.command == "show":
        if not args.name:
            args.name = tui.select_patch(manager.list())
        manager.diff(args.name)


if __name__ == "__main__":
    main()

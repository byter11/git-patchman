# 🔍 git-patchman

A patch/diff management cli + tui plugin for git.

## 📦 Installation

```
pip install git-patchman
```
```

> git patchman -h
usage: cli.py [-h] [-V] {add,delete,apply,show} ...

Manage Git patches with commands to add, delete, and apply patches.

positional arguments:
  {add,delete,apply,show}
                        Available commands
    add                 Add a patch
    delete              Delete a patch
    apply               Apply or revert a patch
    show                View a patch diff

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
```

## 🌟 Features
- 🛠️ Add/Remove/Apply/Revert patches using either CLI commands or a TUI
- 📤 Create patches from a commit, a range of commits or uncommitted changes
  - `git patchman add [name] [commit_id] [--from-changes]`
- 🔍 Omit the patch name to enter TUI mode with search
  - `git patchman show`


## 🧩 Dependencies
- [pytermgui](https://github.com/bczsalba/pytermgui) for the TUI.

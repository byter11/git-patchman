import os
import subprocess
from patchman.tui import PatchTUI


class PatchManager:
    def __init__(self, repo_path="."):
        """
        Initialize the PatchManager class.

        Args:
            repo_path (str): The path to the Git repository.
            Defaults to the current directory.
        """
        self.repo_path = os.path.abspath(repo_path)
        self.patch_dir = os.path.join(self.repo_path, ".git", "patchman")
        self.tui = PatchTUI()
        os.makedirs(self.patch_dir, exist_ok=True)

    def add(self, name: str, commit: str, from_changes: bool):
        """
        Generate a patch from a commit or uncommitted changes
        and save it as a file.

        Args:
            name (str): The name of the patch file (without extension).
            commit (str): The Git commit identifier.
            from_changes (bool): Whether to use uncommitted changes
            instead of a commit.

        Raises:
            ValueError: If the repository path is invalid
            or the Git command fails.
        """
        patch_file_path = os.path.join(self.patch_dir, f"{name}.patch")
        if from_changes:
            # Generate a patch for uncommitted changes
            command = ["diff"]
        else:
            # Generate a patch for the specified commit
            command = ["format-patch", "-1", "--stdout", commit]

        result = subprocess.run(
            command,
            cwd=self.repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        with open(patch_file_path, "w") as patch_file:
            patch_file.write(result.stdout)

        print(f"Patch saved to {patch_file_path}!")

    def delete(self, name: str):
        """
        Delete a patch file with the given name.

        Args:
            name (str): The name of the patch file (without extension).

        Raises:
            FileNotFoundError: If the specified patch file does not exist.
        """
        patch_file_path = os.path.join(self.patch_dir, f"{name}.patch")
        if os.path.exists(patch_file_path):
            os.remove(patch_file_path)
            print(name)
        else:
            raise FileNotFoundError(f"No such patch: {name}")

    def apply(self, name: str, revert: bool = False):
        """
        Apply or revert a patch with the given name.

        Args:
            name (str): The name of the patch file (without extension).
            revert (bool): Whether to revert the patch instead of applying it.
                           Defaults to False.

        Raises:
            FileNotFoundError: If the specified patch file does not exist.
            ValueError: If the Git command fails.
        """
        patch_file_path = os.path.join(self.patch_dir, f"{name}.patch")
        if not os.path.exists(patch_file_path):
            raise FileNotFoundError(f"No such patch: {patch_file_path}")

        # Prepare the git apply command
        command = ["apply"]
        if revert:
            command.append("--reverse")
        command.append(patch_file_path)

        # Run the command
        subprocess.run(
            command,
            cwd=self.repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        action = "Reverted" if revert else "Applied"
        print(f"{action} patch: {name}")

    def __execute_git_command(self, cmd):
        return subprocess.run(
            ["git"] + cmd,
            cwd=self.repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

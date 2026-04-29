import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.status import get_status
from core.repo import init_repo
from core.index import add_files
from core.commit import make_commit
from core.log import get_log
from core.undo import undo_last_commit
from core.exporter import export_repo
from core.importer import import_repo
from core.branch import create_branch, list_branches, switch_branch, delete_branch
from core.merge import merge_branch
from core.push_pull import push_repo, pull_repo

if len(sys.argv) < 2:
    print("""Usage: vcs <command>

Commands:
  init                          Initialize a new repository
  add .                         Stage all files
  commit -m \"message\"          Create a commit
  status                        Show repository status
  log                           Show commit history
  undo                          Undo last commit
  branch                        List branches
  branch <name>                 Create a new branch
  switch <name>                 Switch to a branch
  delete-branch <name>          Delete a branch
  merge <branch>                Merge a branch into current
  export <file.vcs>             Export repository
  import <file.vcs>             Import repository
  push <url> [name]             Push to remote
  pull <url> [name]             Pull from remote
""")
    sys.exit()

command = sys.argv[1]


if command == "init":
    result = init_repo()
    print(result["message"])

elif command == "add":
    if len(sys.argv) < 3 or sys.argv[2] != ".":
        print("Usage: vcs add .")
    else:
        result = add_files()
        print(result["message"], "-", result.get("count", 0), "files")

elif command == "commit":
    if "-m" not in sys.argv:
        print("Usage: vcs commit -m \"message\"")
    else:
        msg_index = sys.argv.index("-m") + 1
        message = sys.argv[msg_index]
        result = make_commit(message)
        print(result["message"])
        if result["success"]:
            print("Commit ID:", result["commit"]["id"])
            print("Branch:", result["commit"].get("branch", "main"))

elif command == "status":
    result = get_status()
    if not result["success"]:
        print(result["message"])
    else:
        print("Branch:", result.get("branch", "main"))
        print("Commit:", result.get("commit_id", "none"))
        print("-" * 40)
        if result["staged"]:
            print("Staged:", result["staged"])
        if result["new"]:
            print("New:", result["new"])
        if result["modified"]:
            print("Modified:", result["modified"])
        if result["deleted"]:
            print("Deleted:", result["deleted"])
        if not any([result["staged"], result["new"], result["modified"], result["deleted"]]):
            print("Working directory clean")

elif command == "log":
    result = get_log()
    if not result["success"]:
        print(result["message"])
    else:
        for c in result["commits"]:
            print(f"commit {c['id']}")
            print(f"    {c['message']}")
            print(f"    {c['timestamp']}")
            if c.get("parent_ids"):
                print(f"    parents: {', '.join(c['parent_ids'])}")
            print()

elif command == "undo":
    result = undo_last_commit()
    print(result["message"])

elif command == "branch":
    if len(sys.argv) == 2:
        result = list_branches()
        if result["success"]:
            for b in result["branches"]:
                prefix = "* " if b["current"] else "  "
                print(f"{prefix}{b['name']}")
    else:
        name = sys.argv[2]
        result = create_branch(name)
        print(result["message"])

elif command == "switch":
    if len(sys.argv) < 3:
        print("Usage: vcs switch <branch-name>")
    else:
        result = switch_branch(sys.argv[2])
        print(result["message"])

elif command == "delete-branch":
    if len(sys.argv) < 3:
        print("Usage: vcs delete-branch <branch-name>")
    else:
        result = delete_branch(sys.argv[2])
        print(result["message"])

elif command == "merge":
    if len(sys.argv) < 3:
        print("Usage: vcs merge <branch-name>")
    else:
        result = merge_branch(sys.argv[2])
        print(result["message"])
        if result["success"]:
            print("Commit ID:", result.get("commit_id"))

elif command == "export":
    if len(sys.argv) < 3:
        print("Usage: vcs export <file.vcs>")
    else:
        result = export_repo(sys.argv[2])
        print(result["message"])

elif command == "import":
    if len(sys.argv) < 3:
        print("Usage: vcs import <file.vcs>")
    else:
        result = import_repo(sys.argv[2])
        print(result["message"])

elif command == "push":
    if len(sys.argv) < 3:
        print("Usage: vcs push <remote-url> [repo-name]")
    else:
        name = sys.argv[3] if len(sys.argv) > 3 else "local"
        result = push_repo(sys.argv[2], name)
        print(result["message"])

elif command == "pull":
    if len(sys.argv) < 3:
        print("Usage: vcs pull <remote-url> [repo-name]")
    else:
        name = sys.argv[3] if len(sys.argv) > 3 else "local"
        result = pull_repo(sys.argv[2], name)
        print(result["message"])

else:
    print(f"Unknown command: {command}")
    print("Run 'vcs' without arguments to see available commands.")
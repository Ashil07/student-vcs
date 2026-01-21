import sys
import os

# Add parent directory to path so we can import core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.status import get_status
from core.repo import init_repo
from core.index import add_files
from core.commit import make_commit

if len(sys.argv) < 2:
    print("Usage: vcs <command>")
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

elif command == "status":
    result = get_status()
    if not result["success"]:
        print(result["message"])
    else:
        print("🟢 New files:", result["new"])
        print("🟡 Modified files:", result["modified"])
        print("🔴 Deleted files:", result["deleted"])


else:
    print("Unknown command")

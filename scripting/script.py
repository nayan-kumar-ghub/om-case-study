# This script validates Terraform plan JSON files to ensure they only contain safe resource changes.

import json
import sys

# Load and parse the tfplan JSON file
def load_plan(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

# Nothing to compare if either state is missing    
def get_changed_fields(before, after):
    if before is None or after is None:
        return []

    changed = []

    # Here keys/tags from both states are checked to catch additions and removals
    all_keys = set(list(before.keys()) + list(after.keys()))

    for key in all_keys:
        before_val = before.get(key)
        after_val  = after.get(key)

        if key == "tags":
            # Tags are nested, so check each tag individually
            if isinstance(before_val, dict) and isinstance(after_val, dict):
                all_tag_keys = set(list(before_val.keys()) + list(after_val.keys()))
                for tag_key in all_tag_keys:
                    if before_val.get(tag_key) != after_val.get(tag_key):
                        changed.append(f"tags.{tag_key}")
            elif before_val != after_val:
                changed.append("tags")
        else:
            if before_val != after_val:
                changed.append(key)

    return changed

def validate_plan(filepath):

    print(f"\n{'='*55}")
    print(f"Validating: {filepath}")
    print(f"{'='*55}")

    plan = load_plan(filepath)

    # Extract the list of resource changes from the plan
    resource_changes = plan.get("resource_changes", [])

    if not resource_changes:
        print("No resource changes found. Safe — nothing to apply.")
        return True

    safe = True

    for resource in resource_changes:

        address = resource.get("address", "unknown")
        change  = resource.get("change", {})
        actions = change.get("actions", [])
        before  = change.get("before")
        after   = change.get("after")

        print(f"\n Resource : {address}")
        print(f"   Actions  : {actions}")

        # No changes planned for this resource
        if actions == ["no-op"]:
            print("ALLOWED: No-op, resource is unchanged.")
            continue

        # Deletions and replacements are not allowed (Main Condition)
        forbidden_actions = [a for a in actions if a in ("delete", "replace")]
        if forbidden_actions:
            print(f"BLOCKED: Destructive action found: {forbidden_actions}")
            safe = False
            continue

        # New resources are always fine
        if actions == ["create"]:
            print("ALLOWED: Creating a new resource.")
            continue

        if "update" in actions:
            changed_fields = get_changed_fields(before, after)
            print(f"Fields that changed: {changed_fields}")

            # Only GitCommitHash tag updates are permitted
            not_allowed = [
                f for f in changed_fields
                if f != "tags.GitCommitHash"
            ]

            if not_allowed:
                print(f"BLOCKED: These fields must not change: {not_allowed}")
                safe = False
            else:
                print("ALLOWED: Only GitCommitHash tag was updated.")
            continue

        # Catch any unexpected action types
        print(f"BLOCKED: Unrecognised action(s): {actions}")
        safe = False

    print(f"\n{'='*55}")
    if safe:
        print("RESULT: Plan is SAFE — apply can proceed.")
    else:
        print("RESULT: Plan is UNSAFE — apply must NOT proceed.")
    print(f"{'='*55}\n")

    return safe

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python script.py <tfplan.json> [tfplan2.json ...]")
        sys.exit(1)

    all_safe = True

    # Validate each file passed in and track overall result
    for filepath in sys.argv[1:]:
        result = validate_plan(filepath)
        if not result:
            all_safe = False

    # Exit code 1 signals failure to CI/CD pipelines
    sys.exit(0 if all_safe else 1)
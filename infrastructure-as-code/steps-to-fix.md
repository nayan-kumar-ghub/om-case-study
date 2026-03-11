# Steps to Fix — Delete 2nd Resource Without Affecting Others

## Exisiting Issue

Earlier Terraform configuration uses `count` to create 5 files:

- local_file.foo[0] → file0.txt
- local_file.foo[1] → file1.txt
- local_file.foo[2] → file2.txt
- local_file.foo[3] → file3.txt
- local_file.foo[4] → file4.txt

And you want to delete second resource (file1.txt) and retain all others.

Simply changing `count = 5` to `count = 4` would delete
`file4.txt` (the last one) instead of `file1.txt` (the 2nd one)
because Terraform re-indexes from the end.

1. step 1 - Move State from count indexes to for_each keys

Rename each resource in TF state from index number to name.
We skip file1.txt because we need to remove this resource.

terraform state mv 'local_file.foo[0]' 'local_file.foo["file0"]'
terraform state mv 'local_file.foo[2]' 'local_file.foo["file2"]'
terraform state mv 'local_file.foo[3]' 'local_file.foo["file3"]'
terraform state mv 'local_file.foo[4]' 'local_file.foo["file4"]'

2. step 2 - Remove 2nd Resource from TF state, file1.txt is removed from Terraform completely.
Terraform will no longer manage or recreate this file.

terraform state rm 'local_file.foo[1]'

3. step 3 - Verify TF State is Updated

terraform state list

local_file.foo["file0"]
local_file.foo["file2"]
local_file.foo["file3"]
local_file.foo["file4"]

4. step 4 - Update main.tf to use for_each
refer main.tf for the code changes

5. step 5 - Verify No Changes after running terraform plan command.

terraform plan
local_file.foo["file3"]: Refreshing state... [id=4094d4c0a6e7a8116b3fdd955ac6fe394f5451f9]
local_file.foo["file0"]: Refreshing state... [id=249fe5aee40516c5c569232c691c2ef2977dfc8c]
local_file.foo["file2"]: Refreshing state... [id=5d4b9c11def79551cec41f2b82305f7ccdd37872]
local_file.foo["file4"]: Refreshing state... [id=6b82f1f329e5eeea23b34725c32d1488c4a56816]

6. Apply the changes

terraform apply 
local_file.foo["file2"]: Refreshing state... [id=5d4b9c11def79551cec41f2b82305f7ccdd37872]
local_file.foo["file4"]: Refreshing state... [id=6b82f1f329e5eeea23b34725c32d1488c4a56816]
local_file.foo["file0"]: Refreshing state... [id=249fe5aee40516c5c569232c691c2ef2977dfc8c]
local_file.foo["file3"]: Refreshing state... [id=4094d4c0a6e7a8116b3fdd955ac6fe394f5451f9]

No changes. Your infrastructure matches the configuration.

Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.
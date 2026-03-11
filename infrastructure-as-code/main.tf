

#variable "files" {
#  default = 5
#}

#resource "local_file" "foo" {
#  count    = var.files
#  content  = "# Some content for file ${count.index}"
#  filename = "file${count.index}.txt"
#}


# Changed from count to for_each
# for_each uses a SET OF NAMES instead of numbers
# This means each resource has a fixed identity
# and removing one does not affect the other resources

variable "files" {
  default = ["file0", "file2", "file3", "file4"]
}

resource "local_file" "foo" {
  for_each = toset(var.files)
  content  = "# Some content for file ${trimprefix(each.key, "file")}"
  filename = "${each.key}.txt"
}

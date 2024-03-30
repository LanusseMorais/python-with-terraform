resource "aws_instance" "this" {
    ami             = var.ami_id
    iam_instance_profile = data.aws_iam_role.iam_ssm.name
    instance_type   = var.instance_type
    subnet_id       = var.subnet_id
    associate_public_ip_address = true
}

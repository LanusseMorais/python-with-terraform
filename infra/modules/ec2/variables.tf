variable ami_id {
    type = string
    default = "ami-033a1ebf088e56e81"
}

variable instance_type {
    type = string
    default = "t2.micro"
}

variable "subnet_id" {
    type = string
}

data "aws_iam_role" "iam_ssm" {
    name = "iam-ssm"
}
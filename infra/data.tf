data "aws_vpc" default {
    default = true
}

data "aws_subnets" default {
    filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
    }
}

data "aws_subnet" "this" {
    id = data.aws_subnets.default.ids[0]
}

data "aws_ssm_parameter" "ssm_ami" {
    name = "ami_super_segura_confia"
}
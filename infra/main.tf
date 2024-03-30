module "ec2_instance" {
    source = "./modules/ec2"
    ami_id = data.aws_ssm_parameter.ssm_ami.value
    # ami_id = "ami-0a7260959324ecbd7"
    subnet_id = data.aws_subnet.this.id
}

resource "aws_ebs_volume" "this" {
    availability_zone = data.aws_subnet.this.availability_zone
    size              = 20
}

resource "aws_volume_attachment" "this" {
    device_name = "/dev/sdb"
    volume_id   = aws_ebs_volume.this.id
    instance_id = module.ec2_instance.id
    force_detach = true
}

output "public_ip" {
    value = "http://${module.ec2_instance.public_ip}:5000"
}
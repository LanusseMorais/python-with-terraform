from python_terraform import Terraform
import configparser
import os
import boto3
from datetime import datetime


# global vars
script_dir = os.path.dirname(os.path.abspath(__file__))
infra_dir = os.path.join(script_dir, '..', 'infra')


def read_config():
    config = configparser.ConfigParser()
    config_path = os.path.join(script_dir, 'rules.ini')
    try:
        config.read(config_path)
    except configparser.Error as e:
        print("Erro ao ler o arquivo de configuração:", e)
        return None
    return config


def deploy_infra():
    tf = Terraform(working_dir=infra_dir)
    return_code, stdout, stderr = tf.apply(skip_plan=True)
    if return_code == 0:
        ouputs = tf.output()
        public_ip = ouputs['public_ip']['value']
        return True, f"Deploy realizado com sucesso. App {public_ip}"
    else:
        return False, f"Algo deu errado ao tentar realizar o deploy!\n{stderr}"


def read_ssm_ami_parameter():
    file_path = os.path.join(infra_dir, 'data.tf')
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'name =' in line:
                parameter_value = line.split('=')[1].strip().strip('" ')
                return parameter_value


def get_latest_parameter_version(parameter_name):
    ssm_client = boto3.client('ssm')
    try:
        response = ssm_client.get_parameter(
            Name=parameter_name, WithDecryption=True)
        ami_id = response['Parameter']['Value']
        # removendo tz pq ele deu showzinho na hora de comparar
        last_modified_date = response['Parameter']['LastModifiedDate'].replace(
            tzinfo=None)
        return ami_id, last_modified_date

    except ssm_client.exceptions.ParameterNotFound:
        print(f'O parâmetro {parameter_name} não foi encontrado.')
        return None, None


def is_deploy_authorized(config_data):
    authorized = config_data['rules'].getboolean('authorized')
    return authorized


def is_ec2_updated():
    tf = Terraform(working_dir=infra_dir)
    return_code, stdout, stderr = tf.plan()
    if return_code == 0:
        return True, "AMI atualizada"
    elif return_code == 2:
        return False, "AMI desatualizada"
    else:
        return stderr, "Algo deu errado ao verificar o estado da EC2!"


def is_new_ami_available():
    ssm_ami_name = read_ssm_ami_parameter()
    ami_id, last_modified_date = get_latest_parameter_version(ssm_ami_name)
    current_date = datetime.now()
    if last_modified_date < current_date:
        return ami_id
    else:
        return False


def check_rules():
    config_data = read_config()
    deploy_authorized = is_deploy_authorized(config_data)
    new_ami_available = is_new_ami_available()
    ec2_updated, ec2_updated_text = is_ec2_updated()
    if new_ami_available and deploy_authorized and not ec2_updated:
        return True, "Todas as regras foram atendidas."
    else:
        reasons = []
        reasons.append(ec2_updated_text)
        if not new_ami_available:
            reasons.append("Não há nova AMI disponível.")
        if not deploy_authorized:
            reasons.append("Deploy não autorizado.")

        return False, ", ".join(reasons)


def main():
    can_deploy, reason = check_rules()
    if can_deploy:
        print(reason)
        print("Iniciando deploy isso pode levar alguns minutos.")
        deploy_success, reason = deploy_infra()
        if not deploy_success:
            print(reason)
        else:
            # print reason duas vezes? Sim são 1:30 da manhã
            print(reason)
    else:
        print("Deploy não executado, motivos: ", reason)


if '__main__' == __name__:
    main()

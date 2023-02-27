import aws_config_exporter as aws
from pathlib import Path
import yaml

cfg_init = yaml.safe_load(Path('definitions.yaml').read_text())

aws_config = {
    "product_type": "public_cloud",
    "cloud_provider": "aws",
    "regions": {}
}

aws_config = aws.orchestrate_export(cfg_init, aws_config)

if len(cfg_init["regions"]) > 1:
    filename = f'multi-region-aws-config.json'
else:
    filename = f'{cfg_init["regions"][0]}-aws-config.json'

# rebuild_aws_network_config(schema=config) # TODO Normalization of data
aws.generate_json_file(filename, aws_config)

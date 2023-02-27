# aws-config-exporter


[![license](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE) [![support](https://img.shields.io/badge/Support%20Level-Community-yellowgreen)](./SUPPORT.md)

## Description
Simple Export Script to output AWS configuration to a JSON File.

### Requirements
* Python 3.9+
* AWS Credentials Profile

### Supported Configuration Exports
* EC2
  * VPC and Related Components
  * Transit Gateway and Related Components
  * Instances
  * Network Interfaces
  * Addresses
  * VPC Endpoints and Endpoint Services
* ELBv2
  * GWLB/NLB/ALB and related components

### Future Support
* ASG and related components

### Example Usage
Currently, no CLI has been added to this project, so all parameters need to be added to the script.

#### Definitions
You can use the _defintions_example.yaml_ to start defining the infrastructure configuration you want to export.
```yaml
---
aws_profile: 'your aws profile'
ec2_includes: # These included keywords are evaluated against the boto3 ec2 library to match only describe methods with these values
  - 'transit_gateway'
  - 'e_route_table'
  - 'e_vpc'
  - 'subnets'
  - 'e_network_interfaces'
  - 'nat_gateways'
  - 'local_gateways'
  - 'vpn_gateways'
  - 'be_security_groups'
  - 'e_addresses'
  - 'e_instances'
  - 'e_volumes'
  - 'customer_gateways'
  - 'internet_gateways'
ec2_exclusions:
  - 'vpc_attribute'
  - '_classic_link'
  - 'service_permissions'
  - 'addresses_attr'
elb_includes: # These included keywords are evaluated against the boto3 elbv2 library to match only describe methods with these values
  - '_load_balancers'
  - 'target_groups'
#  - '_listeners' TODO Evaluate How to Filter/Query and populate
elb_exclusions:
  -
regions:
  - us-west-2:
      dev: # Your Environment Examples: [dev, test, nonprod, prod, qa, eng]
        vpc_ids:
          - 'vpc1id'
          - 'vpc2id'
          - 'vpc3id'
        tgw_ids:
          - 'tgw1id'
        service_names:
          - 'aws vpc endpoint service name'
        resource_types:
          - 'ec2'
          - 'elbv2'
  - us-east-2:
      test: # Your Environment Examples: [dev, test, nonprod, prod, qa, eng]
        vpc_ids:
          - 'vpc1id'
        tgw_ids:
          - 'tgw1id'
        service_names:
          - 'aws vpc endpoint service name'
        resource_types:
          - 'ec2'
          - 'elbv2'
```

```
git clone https://github.com/ancoleman/aws-config-exporter
cd aws-config-exporter
pip install -r requirements.txt
```

```python
#Example from example.py
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

```


## Version History


* 0.1
    * Initial Release

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details
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

#### Paramters
* aws_profile: **_String_** : The AWS Credentials File Profile name 
* schema: **_Dict_** : Schema of the configuration file, default = {}
* keywords: **_List_** : Describe Methods to Include for export
* excludes: **_List_** : Describe Methods to Exclude for export if matching with includes
* region: **_String_** : AWS region to export
* vpc_id: **_String_** : Optional(Your VPC ID) _Recommended_
  * if not specified all VPCs will be exported 
* transit_gateway_id: Optional(Your TGW ID) _Recommended_
  * if not specified all TGW and related components will be exported 
* service_type: **_String_** : Optional('GatewayLoadBalancer')
  * if not specified all endpoint services will be exported 
* attachment_vpc_id: **_String_** : Optional(Your VPC ID)
  * if not specified any services that have attachment.vpc-id filtering will be exported

```
git clone https://github.com/ancoleman/aws-config-exporter
cd aws-config-exporter
pip install -r requirements.txt
```

```python
#Example from example.py
import aws_config_exporter as aws

profiles = ['pso-shared-830100-sso_admin',]

# Network Attributes to describe
ec2_includes = ['transit_gateway',
                'e_route_table',
                'e_vpc',
                'subnets',
                'e_network_interfaces',
                'nat_gateways',
                'local_gateways',
                'vpn_gateways',
                'be_security_groups',
                'e_addresses',
                'e_instances',
                'e_volumes',
                'customer_gateways',
                'internet_gateways'
                ]
ec2_exclusions = ['vpc_attribute',
                  '_classic_link',
                  'service_permissions',
                  'addresses_attr'
                  ]

lb_includes = ['_load_balancers',
               'target_groups',
               '_listerners',
               ]

region = 'us-west-2'
ec2_config = aws.export_aws_config(aws_profile=profiles[0],
                                   schema={},
                                   keywords=ec2_includes,
                                   excludes=ec2_exclusions,
                                   region=region,
                                   patterns={  # TODO FUTURE IMPLEMENTATION
                                       'vpc_id': 'vpc-id',
                                       'attachment_': 'attachment.',
                                       'attachment-': 'attachment.'
                                   },
                                   vpc_id='vpc-x',
                                   transit_gateway_id='tgw-x',
                                   service_type='GatewayLoadBalancer',
                                   attachment_vpc_id='vpc-x'
                                   )

lb_config = aws.export_aws_config(aws_profile=profiles[0],
                                  schema={},
                                  keywords=lb_includes,
                                  resource_type='elbv2',
                                  excludes=[],
                                  region=region,
                                  VpcId='vpc-x',
                                  )
ec2_config.update(lb_config)
filename = f'{region}-aws-config.json'

# rebuild_aws_network_config(schema=config) # TODO Normalization of data
aws.generate_json_file(filename, ec2_config)

```


## Version History


* 0.1
    * Initial Release

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details
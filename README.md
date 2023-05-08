# aws-config-exporter


[![license](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE) [![support](https://img.shields.io/badge/Support%20Level-Community-yellowgreen)](./SUPPORT.md)

## Description
Simple Export Script to output AWS configuration to a JSON File.

### Requirements
* Python 3.7+
* AWS Credentials Profile or Cloud Shell IAM Permissions

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
CLI has been added to this project, you now can pass the definitions filename to the script to run the export.
```bash

#### Definitions
You can use the _defintions_example.yaml_ to start defining the infrastructure configuration you want to export.
```yaml
---
aws_profile: # Leave this blank to use metadata from the AWS Cloud Shell / CLI
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
  - 'e_route_tables'
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
dependencies:
  - 'LoadBalancerArn'
regions:
  - us-east-2:
      dev: # Your Environment Examples: [dev, test, nonprod, prod, qa, eng]
        vpc_ids: # These are the VPC IDs that will be used to filter the describe methods
          - 'vpcid'
          - 'vpcid'
          - 'vpcid'
        tgw_ids: # These are the TGW IDs that will be used to filter the describe methods
          - 'your_tgw_id'
        service_names: # These are the Service Names that will be used to filter the describe methods
          - 'your_service_name'
        resource_types: # These are the Resource Types that will be used to filter the describe methods
          - 'ec2'
          - 'elbv2'
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
```

```bash
git clone https://github.com/ancoleman/aws-config-exporter
cd aws-config-exporter
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

python3 aws_config_exporter.py --f definitions_example.yaml
```


## Version History


* 0.1
    * Initial Release
* 0.2
  * Added CLI

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details
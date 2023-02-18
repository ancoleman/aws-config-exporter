import aws_config_exporter as aws

profiles = ['your_profile',]

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

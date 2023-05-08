import sys
import boto3
import json
import os
import re
import logging
from tqdm import tqdm
import yaml
from pathlib import Path
import click

__author__ = "Anton Coleman"
__copyright__ = "Copyright 2023, Software NGFW Automation"
__credits__ = ["Sean Youngberg"]
__license__ = "MIT"
__version__ = ".2"
__maintainer__ = "Anton Coleman"
__email__ = "acoleman@paloaltonetworks.com"
__status__ = "Community"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


def extract_filter_options(doc, param='Filters'):
    if doc is not None:
        request_syntax_match = re.search(r"\n\s*\*+\s*Request Syntax\s*\*+\s*\n",
                                         str(doc))
        if not request_syntax_match:
            # "Request Syntax" section not found
            print("Request Syntax not found in docstring")
            exit()
        request_syntax_start = request_syntax_match.end()

        response_syntax_match = re.search(r"\n\s*\*+\s*Response Syntax\s*\*+\s*\n",
                                          str(doc))
        if not response_syntax_match:
            # "Response Syntax" section not found
            print("Response Syntax not found in docstring")
            exit()
        request_syntax_end = response_syntax_match.start()
        # Extract the parameter information from the "Request Syntax" section
        request_syntax_text = str(doc)[request_syntax_start:request_syntax_end]
        request_syntax_text = os.linesep.join([s for s in request_syntax_text.splitlines() if s])
        pattern = fr':param {param}:(.*?):param'
        # Search for the pattern in the text
        match = re.search(pattern, request_syntax_text, re.DOTALL)
        if match:
            sub_options = match.group(1)
            option_pattern = r'\* ``(.+?)``'
            options = re.findall(option_pattern, sub_options)
            return options
        else:
            return None


def iterate_dict_cleanup(awsdict):
    """
    This function is used to clean up the dictionary returned from the boto3 describe methods.

    Args:
        awsdict:

    Returns:

    """
    rebuild_dict = {}

    def method_dict_cleanup(parent, child_key):
        new_dict = parent[child_key].copy()
        del parent
        return new_dict

    for k in awsdict:
        rebuild_dict.update({k: {}})
        for child_parent in awsdict[k]:
            cd = method_dict_cleanup(awsdict[k], child_parent)
            rebuild_dict[k].update(cd)
    return rebuild_dict


def filter_data(key, options, func, filter_value=None):
    """
    This function is used to filter the data returned from the boto3 describe methods.

    Args:
        key:
        options:
        func:
        filter_value:

    Returns:

    """
    if filter_value is not None:

        if key in options:
            val = func(
                Filters=[
                    {
                        'Name': key,
                        'Values': [
                            filter_value,
                        ]
                    },
                ]
            )
            if val is not None:
                return val
            else:
                print(val)
                exit()
        else:
            return None


def replace_unique_chars(param_string, replacement_patterns):
    """

    Args:
        param_string: String to inspect
        replacement_patterns:  Pattern to match and replace (dict)

    Returns:

    """
    try:
        for rk in replacement_patterns:
            if rk in param_string:
                result = param_string.replace(rk, replacement_patterns[rk])
        if result is not None:
            return result
    except Exception as e:
        print(e)
        return None


# iterate over the methods of the class
def export_aws_config(schema, keywords, excludes, aws_profile=None, patterns=None, method_match='describe',
                      resource_type='ec2', region='us-east-2', **kwargs):
    """

    Args:
        method_match: Type of method to match against [only describe is currently supported]
        patterns: Dict - Replacement values for unique chars within request params
        resource_type: Type of resource to describe examples are ['ec2','s3','iam','sns']
        aws_profile: The AWS IAM Profile to execute configuration export
        schema: The dictionary schema to apply to configuration export
        excludes: Methods to exclude from describing
        keywords: Methods to describe
        region: AWS Region selection for configuration export

    Returns:

    """
    if aws_profile:
        session = boto3.Session(
            profile_name=aws_profile, region_name=region)
        client = session.client(resource_type)
    else:
        # Assumes Metadata Credentials
        session = boto3.Session(region_name=region)
        client = session.client(resource_type)

    try:
        for method in dir(client):
            # Retrieves all callable methods from the boto3 client object
            if callable(getattr(client, method)):
                name = str(method)
                if 'describe' in name:
                    for keyword in keywords:
                        if keyword in name:
                            # Check if the method is to be excluded from exporting
                            if not any(i in name for i in excludes):
                                method_obj = getattr(client, method)
                                # Extract Docstrings to retrieve filtering options
                                doc = method_obj.__doc__
                                ops = extract_filter_options(doc)
                                config_type = (name.split("describe_"))[1]
                                # Check if filter options exist
                                if bool(kwargs):
                                    for k, v in tqdm(kwargs.items(), desc=f'Retrieving {config_type} for {region}',
                                                     bar_format='{l_bar}{bar:15}{r_bar}{bar:-15b}'):
                                        if ops is not None:
                                            if type(v) == list:
                                                for item in v:
                                                    # Unique for vpc ids following attachments
                                                    # TODO build function to set replacement values for normalization
                                                    k = k.replace('attachment_', 'attachment.')
                                                    k = k.replace('_', '-')
                                                    filtered = filter_data(k, options=ops,
                                                                           func=method_obj, filter_value=item)
                                                    if filtered is not None:
                                                        # Remove unnecessary data
                                                        filtered.pop('ResponseMetadata')
                                                        for fk in filtered:
                                                            if fk in schema:
                                                                if len(filtered[fk]) >= 1:
                                                                    # if name == 'test_attr':
                                                                    #     print(item)
                                                                    #     print(filtered[fk][0])
                                                                    if filtered[fk][0] not in schema[fk]:
                                                                        schema[fk].append(filtered[fk][0])
                                                            else:
                                                                # if name == 'test_attr':
                                                                #     print(item)
                                                                #     for test in filtered[fk]:
                                                                #         print(test)
                                                                schema.update({fk: filtered[fk]})
                                        else:
                                            val = method_obj()
                                            val.pop('ResponseMetadata')
                                            item_list = []
                                            for i in val:
                                                schema.update({i: {}})
                                                for o in val[i]:
                                                    if k in o:
                                                        for vi in v:
                                                            if vi == o[k]:
                                                                item_list.append(o)
                                                                schema[i] = item_list
                                    else:
                                        break
                                else:
                                    val = method_obj()
                                    val.pop('ResponseMetadata')
                                    schema.update(val)
        return schema
    except Exception as e:
        return f'Failed to generate AWS configuration export with error: {e}'


def rebuild_aws_network_config(schema):  # TODO Future Implementation if transforming the data is required
    """

    Args:
        schema: AWS Network Schema

    Returns:

    """

    def get_value(element, key):
        """
        Check if *keys (nested) exists in `element` (dict).
        """
        if not isinstance(element, dict):
            raise AttributeError('keys_exists() expects dict as first argument.')
        if len(key) == 0:
            raise AttributeError('keys_exists() expects at least two arguments, one given.')

        def _get_value(key, dictionary):
            if key in dictionary:
                return dictionary[key]
            for k, v in dictionary.items():
                if isinstance(v, dict):
                    value = _get_value(key, v)
                    if value is not None:
                        return value
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict):
                            value = _get_value(key, item)
                            if value is not None:
                                return value
            return None

        return _get_value(key, element)

    # for k in schema:
    #     if k == 'vpcs':
    #         for vpc in schema[k]['describe_vpcs']['Vpcs']:
    #
    #             pp(get_value(vpc,'VpcId'))
    # print(keys_exists(schema,'VpcId'))


def generate_json_file(filename, config):
    """
        Args:
            config: AWS Configuration Dictionary
            filename: the actual filename to generate for json
    """
    try:
        with open(filename, 'w') as f:
            # Convert dictionary to JSON
            json.dump(config, f, indent=4, default=str, sort_keys=True)
    except Exception as e:
        raise e


def load_definition(filename):
    try:
        config = yaml.safe_load(Path(filename).read_text())
        return config
    except Exception as e:
        sys.exit(1)


@click.command()
@click.option('--f', default='definitions.yaml', help='YAML filename that includes AWS Definitions')
def orchestrate_aws_export(f):
    """
    Orchestrates the AWS Configuration Export by loading the definition file and generating the configuration export,
    then generating the JSON file for the configuration export.

    Args:
        f: filename for the definition file

    Returns:

    """
    config = load_definition(f)
    schema = {
        "product_type": "software_ngfw",
        "cloud_provider": "aws",
        "regions": {}
    }
    for region in config["regions"]:
        for rk in region:
            logger.info(f'Accessing region: {rk}')
            schema['regions'].update({rk: {}})
            environments = region[rk]
            for env in environments:
                logger.info(f'Retrieving environment: {env}')
                attrs = environments[env]
                schema['regions'][rk].update({env: {}})

                if 'resource_types' in attrs:
                    for rtype in attrs['resource_types']:
                        logger.info(f'Accessing AWS Client Type: {rtype}')
                        if rtype == 'ec2':
                            # TODO Add Defaults if data is missing from defintion
                            includes = config["ec2_includes"]
                            excludes = config["ec2_exclusions"]
                            filters = {
                                'vpc_id': attrs['vpc_ids'],
                                'transit_gateway_id': attrs['tgw_ids'],
                                'service_name': attrs['service_names'],
                                'attachment_vpc_id': attrs['vpc_ids'],
                            }
                        if rtype == 'elbv2':
                            # TODO Add Defaults if data is missing from defintion
                            includes = config["elb_includes"]
                            filters = {
                                'VpcId': attrs['vpc_ids']
                            }
                            excludes = []
                        try:
                            result = export_aws_config(aws_profile=config["aws_profile"],
                                                       schema={},
                                                       keywords=includes,
                                                       excludes=excludes,
                                                       region=rk,
                                                       resource_type=rtype,
                                                       **filters
                                                       )

                            schema['regions'][rk][env].update(result)
                            logger.info(
                                f'Completed configuration retrieval for environment **{env}** using the **{rtype}** '
                                f'client')
                        except Exception as e:
                            print(e)
                            sys.exit(1)

                else:
                    raise f'No aws resource type was specified in the definition'

    if len(config["regions"]) > 1:
        filename = f'multi-region-aws-config.json'
        generate_json_file(filename, schema)
        print(f'Generated {filename}')
    else:
        filename = f'{list(config["regions"][0].keys())[0]}-aws-config.json'
        generate_json_file(filename, schema)
        print(f'Generated {filename}')


if __name__ == '__main__':
    try:
        orchestrate_aws_export()
    except Exception as e:
        print(e)
        sys.exit(1)

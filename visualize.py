import networkx as nx
import json
from pyvis.network import Network
from pyvis.options import EdgeOptions
from graphviz import Digraph
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


class Visualizer:
    """
    Visualize Cloud Environment Network Data
    """
    def __init__(self):
        self.subnet_name = None
        self.subnet_id = None
        self.vpc_name = None
        self.vpc_id = None
        self.environment_name = None
        self._icons = None
        self._graph = nx.Graph()
        self._config = None
        self._base_ico_url = None
        self._html_file = None
        self._flowchart_file = None
        self._env_data = None
        self._provider = None
        self._customer = None
        # self.base_ico_url = 'https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/master/dist/'

    def get_base_ico_url(self):
        return self._base_ico_url

    def set_base_ico_url(self, url):
        self._base_ico_url = url

    def set_config(self, data):
        """
        Set the config data
        Args:
            data:

        Returns:

        """
        self._config = data
        if 'cloud_provider' in self._config:
            self._provider = self._config['cloud_provider']
            self.set_icons()
        if 'customer' in self._config:
            self._customer = self._config['customer']
        else:
            self._customer = 'customer'

    def get_config(self):
        return self._config

    def set_html_file(self, filepath):
        """
        Set the pyvis html file path
        Args:
            filepath:

        Returns:

        """
        self._html_file = filepath

    def set_flowchart_file(self, filepath):
        """
        Set the flowchart file path
        Args:
            filepath:

        Returns:

        """
        self._flowchart_file = filepath

    def set_env_data(self, data):
        """
        Set the environment data
        Args:
            data:

        Returns:

        """
        self._env_data = data

    def add_node_edge(self, node, edge_k, edge_v, title=None, shape='dot', image=None, size=None, group=None):
        """
        Add node and edges to the graph
        Args:
            node:
            edge_k:
            edge_v:
            title:
            shape:
            image:
            size:
            group:

        Returns:

        """
        try:
            if shape == 'image':
                self._graph.add_node(node, title=title, shape=shape, image=image, group=group)
            else:
                self._graph.add_node(node, title=title, shape=shape, group=group)
            if edge_k:
                self._graph.add_edge(edge_k, edge_v)
            if size is not None:
                self._graph.nodes[node]['value'] = size
        except Exception as e:
            logger.error(f'Error adding node: {node} to graph: {e}')

    def lookup_if_tag_exists(self, tags, key, failback=None):
        """
        Lookup a tag in a list of tags
        Args:
            tags:
            key:
            failback:

        Returns:

        """
        try:
            for tag in tags:
                if tag['Key'] == key:
                    return tag['Value']
                else:
                    return failback
        except Exception as e:
            logger.error(f'Error looking up tag: {e}')

    def format_table(self, kwargs, same_line=False):
        """
        Format a string table from a dictionary
        Args:
            kwargs:
            same_line:

        Returns:

        """
        table = ""
        try:
            if same_line:
                count = 0
                filter_range = len(kwargs)
                for k, v in kwargs.items():
                    table += f"{k}: {v} | "
                    if count >= filter_range:
                        table += "\n"
                table.rstrip()
                return table
            else:
                for k, v in kwargs.items():
                    table += f"{k}: {v} \n"
                table.rstrip()
                return table
        except Exception as e:
            logger.error(f'Error formatting table: {e}')

    def process_virtual_networks(self):
        """
        Process virtual networks
        Args:
            config:
            provider:

        Returns:

        """
        logger.info(f'Processing virtual networks for {self._provider}')
        if self._provider == "aws":
            for vpc in self._env_data['Vpcs']:
                self.vpc_id = vpc['VpcId']
                self.vpc_name = self.lookup_if_tag_exists(vpc['Tags'], 'Name', self.vpc_id)
                table = self.format_table({'cidr': vpc['CidrBlock'], 'id': self.vpc_id})
                self.add_node_edge(self.vpc_name, self.environment_name, self.vpc_name, title=table, shape='image',
                                   image=self._icons["vpc_ico"], size=40)
                self.process_subnets()
            logger.info(f'Completed processing virtual networks for {self._provider}')
        elif self._provider == "azure":
            pass
        elif self._provider == "google":
            pass
        else:
            logger.error(f'Failed to process virtual networks for {self._provider}, either provider not supported or '
                         f'invalid configuration')
            raise

    def process_subnets(self):
        """
        Process subnets
        Args:
            config:
            provider:

        Returns:

        """
        if self._provider == "aws":
            logger.info(f'Processing subnets for {self.vpc_name}:{self.vpc_id}')
            for subnet in self._env_data['Subnets']:
                self.subnet_id = subnet['SubnetId']
                self.subnet_name = self.lookup_if_tag_exists(subnet['Tags'], 'Name', self.subnet_id)
                if subnet['VpcId'] == self.vpc_id:
                    az = subnet['AvailabilityZone']
                    table = self.format_table({'cidr': subnet['CidrBlock'], 'id': subnet['SubnetId']})
                    self.add_node_edge(self.subnet_name, self.vpc_name, self.subnet_name, title=table, shape='image',
                                       image=self._icons["private_subnet_ico"], size=30, group=self.vpc_id)
                    self.add_node_edge(az, self.subnet_name, az, shape='image',
                                       image=self._icons["zone_ico"], size=30)
                    self.process_instances()
                    self.process_route_tables()
            logger.info(f'Completed processing subnets for {self.vpc_name}:{self.vpc_id}')
        elif self._provider == "azure":
            pass
        elif self._provider == "google":
            pass
        else:
            logger.error(f'Provider: {self._provider} not supported')
            raise

    def process_route_tables(self):
        """
        Process route tables
        Args:
            config:
            provider:

        Returns:

        """
        if self._provider == "aws":
            logger.info(f'Processing route tables for {self.subnet_name}:{self.subnet_id}')
            for rt in self._env_data['RouteTables']:
                rt_associations = rt['Associations'][0]
                if rt_associations['AssociationState']['State'] == 'associated':
                    if 'SubnetId' in rt_associations:
                        if rt_associations['SubnetId'] == self.subnet_id:
                            rt_name = self.lookup_if_tag_exists(rt['Tags'], 'Name',
                                                                rt['RouteTableId'])
                            if rt_name == self.subnet_name:
                                rt_name = f"{rt_name}_rt"
                            table = self.format_table({'id': rt['RouteTableId']})
                            for route in rt['Routes']:
                                result = {key: value for key, value in route.items() if
                                          'Gateway' in key}
                                table += self.format_table(
                                    {'destination': route['DestinationCidrBlock']},
                                    same_line=True)
                                if result:
                                    first_key, first_value = next(iter(result.items()))
                                    table += self.format_table({'target': first_value})
                            self.add_node_edge(node=rt_name, edge_k=self.subnet_name, edge_v=rt_name,
                                               title=table,
                                               shape='image', image=self._icons["rt_icon"], size=20)
            logger.info(f'Completed processing route tables for {self.subnet_name}:{self.subnet_id}')
        elif self._provider == "azure":
            pass
        elif self._provider == "google":
            pass
        else:
            logger.error(f'Provider: {self._provider} not supported')
            raise

    def process_instances(self):
        """
        Process instances

        Returns:

        """
        if self._provider == "aws":
            logger.info(f'Processing instances for {self._provider}')
            for reservation in self._env_data['Reservations']:
                for instance in reservation['Instances']:
                    # if instance['State']['Name'] == 'running': # TODO enforce only running instances future state
                    instance_id = instance['InstanceId']
                    instance_name = self.lookup_if_tag_exists(instance['Tags'], 'Name', instance_id)
                    instance_type = instance['InstanceType']
                    instance_az = instance['Placement']['AvailabilityZone']
                    table = self.format_table({'id': instance_id,
                                               'type': instance_type,
                                               'ami': instance['ImageId'],
                                               'keyname': instance['KeyName'],
                                               'az': instance_az,
                                               'state': instance['State']['Name'],
                                               'private_ip': instance['PrivateIpAddress']})
                    if 'fw' in instance_name or 'vmseries' in instance_name or 'firewall' in instance_name:
                        instance_ico = self._icons["vmseries"]
                    if 'pano' in instance_name or 'mgmt' in instance_name:
                        instance_ico = self._icons["panorama"]
                    else:
                        instance_ico = self._icons["instance_ico"]
                    self.add_node_edge(node=instance_name, edge_k=self.vpc_name, edge_v=instance_name,
                                       title=table, shape='image', image=instance_ico, size=30)
            logger.info(f'Completed processing instances for {self._provider}')
        elif self._provider == "azure":
            pass
        elif self._provider == "google":
            pass
        else:
            logger.error(f'Provider: {self._provider} not supported')
            raise

    def process_zones(self):
        """
        Process zones
        Returns:

        """
        if self._provider == "aws":
            pass
        elif self._provider == "azure":
            pass
        elif self._provider == "google":
            pass
        else:
            logger.error(f'Provider: {self._provider} not supported')
            raise

    def apply_network_attributes(self):
        pass

    def set_icons(self):
        self._icons = {
            "region_ico": f'{self._base_ico_url}{self._provider}/region.png',
            "vpc_ico": f'{self._base_ico_url}{self._provider}/vpc.png',
            "public_subnet_ico": f'{self._base_ico_url}{self._provider}/public_subnet.png',
            "private_subnet_ico": f'{self._base_ico_url}{self._provider}/private_subnet.png',
            "rt_icon": f'{self._base_ico_url}{self._provider}/route_table.png',
            "zone_ico": f'{self._base_ico_url}{self._provider}/zone.png',
            "env_ico": f'{self._base_ico_url}general/environment.png',
            "instance_ico": f'{self._base_ico_url}{self._provider}/instance.png',
            "vmseries": f'{self._base_ico_url}paloaltonetworks/vmseries.png',
            "cnseries": f'{self._base_ico_url}paloaltonetworks/cnseries.png',
            "panorama": f'{self._base_ico_url}paloaltonetworks/vmpanorama.png'
        }

    def map_network_config(self):
        logger.info('Mapping network configuration')
        try:
            for rk, rv in self._config['regions'].items():
                self.add_node_edge(rk, None, None, shape='image', image=self._icons["region_ico"], size=50)
                for ek, ev in rv.items():
                    self.set_env_data(ev)
                    self.environment_name = ek
                    self.add_node_edge(ek, rk, ek, shape='image', image=self._icons["env_ico"], size=40)
                    self.process_virtual_networks()
            logger.info('Completed mapping network data')
        except Exception as e:
            logger.error(f'Error mapping network data: {e}')
            raise

    def render_web_visual(self):
        logger.info('Rendering web visuals')
        try:
            net = Network(notebook=True, cdn_resources='remote', height='800px', width='100%',
                          heading=f'AWS Network for {self._customer}', bgcolor='#7ed9ed', font_color='black',
                          directed=True, layout=True, filter_menu=True)
            net.from_nx(self._graph)
            edge_options = EdgeOptions()
            edge_options.color.highlight = 'red'
            net.set_edge_smooth('dynamic')
            for node in net.nodes:
                node['color'] = 'orange'
            for edge in net.edges:
                edge['color'] = 'white'
            net.force_atlas_2based(overlap=1)
            net.show(self._html_file)
            logging.warning('WORKAROUND: Removing secondary header from html file')
            html_str = re.sub(r'<center>.+?<\/h1>\s+<\/center>', '', net.html, 1, re.DOTALL)
            h = open(self._html_file, 'w')
            h.write(html_str)
            h.close()
        except Exception as e:
            logger.error(f'Error rendering web visuals: {e}')
            raise

    def render_flowchart(self):
        """
        Render flowchart
        Returns:

        """
        logger.info('Rendering flowchart')
        try:
            dot = Digraph(comment='Flowchart')
            dot.format = 'png'
            for node in self._graph.nodes:
                dot.node(node)
            for edge in self._graph.edges:
                dot.edge(edge[0], edge[1])
            dot.render(self._flowchart_file, view=True)
        except Exception as e:
            logger.error(f'Error rendering flowchart: {e}')
            raise


def main():
    def load_json(filepath):
        with open(filepath) as f:
            data = json.load(f)
        return data

    network = Visualizer()
    network.set_base_ico_url('https://raw.githubusercontent.com/ancoleman/graph-icons/main/')
    network.set_html_file('aws_network_diagram.html')
    network.set_flowchart_file('aws_network_diagram.png')
    network.set_config(load_json('multi-region-aws-config_old.json'))
    network.map_network_config()
    network.render_web_visual()


if __name__ == '__main__':
    main()

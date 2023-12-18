# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod
from collections import defaultdict
import re
import datetime
from typing import Dict, Any, Optional, Union, List
import xml.etree.ElementTree as ElementTree


class TransformerException(Exception):
    pass


class AbstractTransformer(ABC):
    """Abstract class for implementation transformers"""
    key = None

    def __init__(self, ignore_errors: bool = False,
                 removing_types: bool = False):
        self.ignore_errors = ignore_errors
        self.removing_types = removing_types

    def transform_node(self, node_data: Dict) -> Dict:
        if self.check_node_data(node_data):
            if self.ignore_errors:
                node_data['#text'] = self.get_safe_value(node_data)
            else:
                node_data['#text'] = self.get_value(node_data)
            node_data = self.remove_type_from_node_data(node_data)
        return node_data

    def check_node_data(self, node_data: Dict) -> bool:
        if node_data.get("@type") != self.key:
            return False
        if "#text" not in node_data:
            return False
        return True

    def get_safe_value(self, node_data: Dict) -> Any:
        try:
            value = self.get_value(node_data)
        except TransformerException:
            value = node_data.get("#text")
        return value

    def get_value(self, node_data: Dict) -> Any:
        try:
            return self.get_value_or_raise_exception(node_data)
        except Exception as e:
            raise TransformerException(
                '{0}: {1}'.format(self.__class__, str(e)))

    @abstractmethod
    def get_value_or_raise_exception(self, node_data: Dict) -> Any:
        pass

    def remove_type_from_node_data(self, node_data: Dict) -> Dict:
        if self.removing_types:
            del node_data["@type"]
        return node_data

    def set_ignore_errors(self, ignore_errors: bool) -> None:
        self.ignore_errors = ignore_errors

    def set_removing_types(self, removing_types: bool) -> None:
        self.removing_types = removing_types


class IntegerTransformer(AbstractTransformer):
    """Transformer for integers"""
    key = "integer"

    def get_value_or_raise_exception(self, node_data: Dict) -> int:
        return int(node_data['#text'])


class BoolTransformer(AbstractTransformer):
    """Transformer for booleans"""
    key = "bool"

    def get_value_or_raise_exception(self, node_data: Dict) -> bool:
        value = node_data['#text'].lower()
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
        else:
            raise TypeError('Value has to be "true" or "false"')
        return value


class DateTimeTransformer(AbstractTransformer):
    """Transformer for datetime.datetime"""
    key = "datetime"
    datetime_format = "%Y-%m-%dT%H:%M:%SZ"

    def get_value_or_raise_exception(
            self, node_data: Dict) -> datetime.datetime:
        value = node_data['#text'].lower()
        value = datetime.datetime.strptime(value, self.datetime_format)
        return value

    def set_datetime_format(self, datetime_format: str) -> None:
        self.datetime_format = datetime_format


class PullTransformers:
    def __init__(self, *transformers):
        self.transformers = dict()
        self.add_transformers(*transformers)

    def add_transformers(self, *transformers) -> None:
        for transformer in transformers:
            self.__register_transformer(transformer)

    def __register_transformer(
            self, transformer: Union[AbstractTransformer, type]) -> None:
        transformer_instance = self.__get_transformer_instance(transformer)
        if isinstance(transformer_instance, AbstractTransformer):
            self.transformers[transformer_instance.key] = transformer_instance

    @staticmethod
    def __get_transformer_instance(
            transformer: Union[AbstractTransformer, type]
            ) -> AbstractTransformer:
        if isinstance(transformer, type):
            return transformer()
        return transformer

    def transform_node(self, node_data: Dict) -> Dict:
        key = self.get_key(node_data)
        if key is not None:
            transformer = self.get_transformer(key)
            if transformer is not None:
                return transformer.transform_node(node_data)
        return node_data

    @staticmethod
    def get_key(node_data: Dict) -> Optional[str]:
        if '@type' in node_data:
            return node_data['@type']

    def get_transformer(self, key: str) -> Optional[AbstractTransformer]:
        if key in self.transformers:
            return self.transformers[key]
        return None

    def set_ignore_errors(self, ignore_errors: bool) -> None:
        for transformer_key in self.transformers:
            self.transformers[transformer_key].set_ignore_errors(
                ignore_errors
            )

    def set_removing_types(self, removing_types: bool) -> None:
        for transformer_key in self.transformers:
            self.transformers[transformer_key].set_removing_types(
                removing_types
            )


class XmlToDict(object):
    """Class to work with xml.etree.ElementTree objects"""
    _pull_transformers = None

    def __init__(self, node: ElementTree, ignore_namespace: bool = False):
        """
        Init instance
        :param node: XML object
        :param ignore_namespace: removing namespace from tags
        """
        self.node = node
        self.ignore_namespace = ignore_namespace
        self.child_nodes = list()

    def get_dict(self) -> Dict:
        """
        Extract data from xml.etree.ElementTree object
            which has been passed during initialization of an instance
        :return: extracted data as a python dict
        """
        tag = self.get_tag()
        self.child_nodes = self._get_child_nodes()
        if self._is_single_node():
            value = self._get_dict_from_single_node()
        else:
            value = self._get_dict_from_node_with_children()
        return {tag: value}

    def get_tag(self) -> str:
        """
        Get a tag of the current node.
            If ignore_namespace is True then
            namespace will be removed from a tag.
        :return: a tag
        """
        tag = self.node.tag
        if self.ignore_namespace:
            tag = re.sub(r'{[^}]+}', '', tag)
        return tag

    def _get_child_nodes(self) -> List:
        """
        Get child nodes of xml.etree.ElementTree object
            which has been passed during initialization of an instance
            as XmlToDict instances.
            All options (ignore_namespace, transformers) of the current class
            will be used for children nodes
        :return: List of XmlToDict instances
        """
        child_nodes = []
        for child_node in self.node:
            xml_to_dict_node = XmlToDict(
                child_node, ignore_namespace=self.ignore_namespace)
            if self._pull_transformers is not None:
                xml_to_dict_node.use_pull_transformers(
                    self._pull_transformers)
            child_nodes.append(xml_to_dict_node)
        return child_nodes

    def _is_single_node(self) -> bool:
        """
        If node has no child nodes, this node is a single node
        :return: result of check
        """
        return True if not self.child_nodes else False

    def _get_dict_from_single_node(self) -> Dict:
        """
        Extract data from the current node, ignoring child nodes, and
            transform result, using instance transformers
        :return: Python dict with data node
        """
        data_node = self._get_single_data_node()
        transformed_data_node = self._transform_node(data_node)
        grouped_data_node = self._group_single_node_data(transformed_data_node)
        return grouped_data_node

    def _get_single_data_node(self) -> Dict:
        """
        Extract value and attributes of the current node
        :return: Python dict with data node
        """
        attributes = self._get_attributes()
        node_value = {'#text': self._get_value()}
        data_node = {**attributes, **node_value}
        return data_node

    def _get_value(self) -> Union[str, None]:
        """
        Get node value
        :return: node value
        """
        value = self.node.text
        if value is not None:
            value = value.strip()
        return value

    def _transform_node(self, node_data: Dict) -> Dict:
        """
        Transform data node, using instance transformers
        :param node_data: data for transformation
        :return: transformed data
        """
        if self._pull_transformers is not None:
            node_data = self._pull_transformers.transform_node(node_data)
        return node_data

    @staticmethod
    def _group_single_node_data(node_data: Dict) -> Dict:
        """
        Group node data if node data has just a value
        xmltodict3.XmlToDict._group_single_node_data({'#text': '1'})
        '1'
        :param node_data: node data to group
        :return:grouped node data
        """
        if tuple(node_data.keys()) == ('#text',):
            node_data = node_data['#text']
        return node_data

    def _get_dict_from_node_with_children(self) -> Dict:
        """
        Get node attributes and data from child nodes
        :return: node data
        """
        attributes = self._get_attributes()
        children_data = self._get_children_data()
        value = {**children_data, **attributes}
        return value

    def _get_attributes(self) -> Dict:
        """
        Get node attributes.
            Attributes are marked with "@" in the attribute name
        :return: node attributes as dict
        """
        attributes = dict()
        for attribute_name in self.node.attrib:
            key = '@' + attribute_name
            attributes[key] = self.node.attrib[attribute_name]
        return attributes

    def _get_children_data(self) -> Dict:
        """
        Get data from child nodes
        :return: nodes data as dict
        """
        node_data = defaultdict(list)
        for child_node in self.child_nodes:
            tag = child_node.get_tag()
            node_data[tag].append(child_node.get_dict()[tag])
        node_data = self._group_children_data(node_data)
        return node_data

    @staticmethod
    def _group_children_data(children_data: defaultdict) -> Dict:
        """
         children_data = defaultdict(list)
         children_data['tag1'].append({'#value': None})
         children_data['tag2'].append({'#value': None})
         children_data['tag2'].append({'#value': '111'})
         xmltodict3.XmlToDict._group_children_data(children_data)
        {'tag1': {'#value': None},
        'tag2': [{'#value': None}, {'#value': '111'}]}
        :param children_data: data from child nodes
        :return: grouped data
        """
        grouped_data = dict()
        for tag in children_data:
            sub_node_data = children_data[tag]
            if len(sub_node_data) == 1:
                grouped_data[tag] = sub_node_data[0]
            else:
                grouped_data[tag] = sub_node_data
        return grouped_data

    def use_pull_transformers(
            self, pull_transformers: PullTransformers) -> None:
        """
        Set up pull_transformation for data transformation
        :param pull_transformers: PullTransformers instance
        """
        if isinstance(pull_transformers, PullTransformers):
            self._pull_transformers = pull_transformers


class XmlTextToDict:
    """Class to work with strings which contain XML"""
    def __init__(self, xml_text: str, ignore_namespace: bool = False):
        """
        Init instance
        :param xml_text: string with XML
        :param ignore_namespace: removing namespace from tags
        """
        self.xml_text = xml_text
        self.ignore_namespace = ignore_namespace
        self._pull_transformers = None

    def get_dict(self) -> Dict:
        """
        Extract data which has been passed during initialization of an instance
        :return: extracted data as a python dict
        """
        xml_to_dict_node = self.get_xml_to_dict_node()
        if self._pull_transformers is not None:
            xml_to_dict_node.use_pull_transformers(
                self._pull_transformers)
        return xml_to_dict_node.get_dict()

    def get_xml_to_dict_node(self) -> XmlToDict:
        """
        Prepare a XmlToDict instance
        :return: a XmlToDict instance with data
        """
        root_node = ElementTree.fromstring(self.xml_text)
        xml_to_dict_node = XmlToDict(
            root_node, ignore_namespace=self.ignore_namespace)
        return xml_to_dict_node

    def use_pull_transformers(
            self, pull_transformers: PullTransformers) -> None:
        """
        Set up pull_transformation for using into XmlToDict object
        :param pull_transformers: PullTransformers instance
        """
        if isinstance(pull_transformers, PullTransformers):
            self._pull_transformers = pull_transformers


class XmlFileToDict:
    """Class to work with XML files"""
    def __init__(self, file_path: str, ignore_namespace: bool = False):
        """
        Init instance
        :param file_path: path to XML file
        :param ignore_namespace: removing namespace from tags
        """
        self.file_path = file_path
        self.ignore_namespace = ignore_namespace
        self._pull_transformers = None

    def get_dict(self) -> Dict:
        """
        Prepare a XmlToDict instance
        :return: a XmlToDict instance with data
        """
        tree_node = ElementTree.parse(self.file_path)
        root_node = tree_node.getroot()
        xml_to_dict_node = XmlToDict(
            root_node, ignore_namespace=self.ignore_namespace)
        return xml_to_dict_node.get_dict()


DefaultTransformerList = [
    IntegerTransformer, BoolTransformer, DateTimeTransformer]

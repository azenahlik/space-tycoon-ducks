# coding: utf-8

"""
    Space Tycoon

    Space Tycoon server.  # noqa: E501

    OpenAPI spec version: 1.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class Player(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'name': 'str',
        'color': 'Color',
        'net_worth': 'NetWorth'
    }

    attribute_map = {
        'name': 'name',
        'color': 'color',
        'net_worth': 'netWorth'
    }

    def __init__(self, name=None, color=None, net_worth=None):  # noqa: E501
        """Player - a model defined in Swagger"""  # noqa: E501
        self._name = None
        self._color = None
        self._net_worth = None
        self.discriminator = None
        self.name = name
        self.color = color
        self.net_worth = net_worth

    @property
    def name(self):
        """Gets the name of this Player.  # noqa: E501


        :return: The name of this Player.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Player.


        :param name: The name of this Player.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def color(self):
        """Gets the color of this Player.  # noqa: E501


        :return: The color of this Player.  # noqa: E501
        :rtype: Color
        """
        return self._color

    @color.setter
    def color(self, color):
        """Sets the color of this Player.


        :param color: The color of this Player.  # noqa: E501
        :type: Color
        """
        if color is None:
            raise ValueError("Invalid value for `color`, must not be `None`")  # noqa: E501

        self._color = color

    @property
    def net_worth(self):
        """Gets the net_worth of this Player.  # noqa: E501


        :return: The net_worth of this Player.  # noqa: E501
        :rtype: NetWorth
        """
        return self._net_worth

    @net_worth.setter
    def net_worth(self, net_worth):
        """Sets the net_worth of this Player.


        :param net_worth: The net_worth of this Player.  # noqa: E501
        :type: NetWorth
        """
        if net_worth is None:
            raise ValueError("Invalid value for `net_worth`, must not be `None`")  # noqa: E501

        self._net_worth = net_worth

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(Player, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Player):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other

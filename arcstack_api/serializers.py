import json

from django.utils.module_loading import import_string

from .conf import settings


class JsonSerializer:
    """
    A utility class for serializing and deserializing JSON data.
    """

    @classmethod
    def serialize(cls, data):
        """
        Serialize the data to a JSON-formatted string.

        :return: JSON string representation of the data.
        """
        return json.dumps(data, cls=cls._get_default_encoder())

    @classmethod
    def deserialize(cls, data):
        """
        Deserialize a JSON-formatted string to a Python object.

        :param data: JSON string to deserialize.
        :return: Deserialized Python object.
        """
        return json.loads(data)

    @classmethod
    def is_json_serializable(cls, data):
        """
        Check if the data can be serialized to JSON.

        :param data: Data to check for JSON serialization.
        :return: True if data is JSON serializable, False otherwise.
        """
        try:
            cls.serialize(data)
        except TypeError:
            return False
        return True

    @classmethod
    def _get_default_encoder(cls):
        """
        Retrieve the default JSON encoder from settings.

        :return: Default JSON encoder class.
        """
        return import_string(settings.API_JSON_ENCODER)

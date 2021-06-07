import json
import os


class Settings:
    """Class handling the settings of the app and the profile.
    Contains all the top level settings values as class attributes

    Attributes:
        path (string): path to the settings.json
        + All the settings fields

    Args:
        path (str, optional): path to settings.json, defaults to 'settings/settings.json'
    """
    def __init__(self, path="settings\\settings.json"):
        self.settings_path = path
        self.load(path)

    def load(self, path=None):
        """Load a settings file.

        Args:
            path (str, optional): path to settings.json
        
        Returns:
            settings (Settings): this object with the attributed loaded
        """
        path = self.settings_path if path is None else path
        with open(path, "r") as settings_file:
            # set all the settings as class attributes
            for key, value in json.load(settings_file).items():
                value = self._normalise_profile(value) if key == "profile" else value
                setattr(self, key, value)
        return self

    def _normalise_profile(self, settings_profile_value):
        """Make sure the 'profile' value in the settings is valid.

        Args:
            settings_profile_value (str or dict): 'profile' value set in the settings file

        Returns:
            profile (Profile): parsed profile object

        Raises:
            ValueError: if the argument is not string or dictionary
            NotImplementedError: if the argument is None, a default value will be set in the future
        """
        if isinstance(settings_profile_value, str):  # must be a path relative to the settings file
            settings_dir = os.path.dirname(self.settings_path)
            profile_path = os.path.join(settings_dir, settings_profile_value)
            with open(profile_path, "r") as profile_file:
                return Profile(json.load(profile_file))
        elif isinstance(settings_profile_value, dict):
            return Profile(settings_profile_value)
        elif settings_profile_value is None:
            raise NotImplementedError("No profile specified in settings, there are no default implemented yet")
        else:
            raise ValueError("Profile value in the settings must be either a json or a path to a json file")

    def get_pixel_list(self, index):
        """Return a map item by the index

        Args:
            index (int): index of the map

        Returns:
            coords (list): list of pixel coordinates

        Raises:
            KeyError: index not in the map

        """
        coords = self.profile.map.get(str(index), None)
        if coords is None:
            raise KeyError(f"Key {index} does not appear in the map")
        return coords["pixels"]


class Profile:
    """Class containing the profile json data.

    Args:
        json_data (dict): contents of the profile json file
    """
    def __init__(self, json_data):
        self._validate(json_data)
        json_data = self._normalise(json_data)
        for key, value in json_data.items():
            setattr(self, key, value)
    
    def _validate(self, json_data):
        """Validate the profile json.

        Args:
            json_data (dict): contents of the profile json file
        
        Raises:
            KeyError: missing key in the input data
            TypeError: value has a wrong type
        """
        for required_key in ["description", "map"]:
            if required_key not in json_data:
                raise KeyError(f"Field missing from the profile: '{required_key}'")

        for key, value in json_data.get("map").items():
            if not key.isdigit():
                raise KeyError(f"Illegal map key: '{key}'. Must be an integer.")
            if not isinstance(value, (dict, list)):
                raise TypeError(f"Illegal map value: '{value}'.")
        
    def _normalise(self, json_data):
        """Normalise the values.

        Args:
            json_data (dict): contents of the profile json file
        
        Returns:
            json_data (dict): better, improved contents of the profile json file
        """
        for map_index, map_value in json_data.get("map").items():
            if isinstance(map_value, list):
                json_data["map"][map_index] = {"pixels": map_value}
            elif "pixels" in map_value:
                continue
            elif "bbox" in map_value:

                if map_value["bbox"][0] <= map_value["bbox"][2]:
                     map_value["bbox"][2] = map_value["bbox"][0] + 1
                if map_value["bbox"][1] <= map_value["bbox"][3]:
                     map_value["bbox"][3] = map_value["bbox"][1] + 1
                json_data["map"][map_index]["pixels"] = [
                        (x, y)
                        for x in range(map_value["bbox"][0], map_value["bbox"][2])
                        for y in range(map_value["bbox"][1], map_value["bbox"][3])
                    ]

        return json_data

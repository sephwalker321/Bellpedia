import yaml
import geopy.distance
from pyproj import Proj


def load_yaml(filename):
    """ 
    Load yaml into python dict
    
    Parameters
    ----------
        filename: str
            absolute path of .yaml file 

    Returns
    -------
        YAML: dict
            Required file

    """
    with open(filename, "r") as stream:
        try:
            YAML = yaml.safe_load(stream)
            return YAML
        except yaml.YAMLError as exc:
            print(exc)
    return
    

def convert_distance(
        distance_unit,
    ):
    """ 
    Convert meters into unit of choice.
    
    Parameters
    ----------
        distance_unit: str
            desired unit

    Returns
    -------
        unit_factor: float
            rescaling factor e.g. x[meters] / unit_factor = y[distance_unit]

    """
    if distance_unit in ["mi","mile","miles"]:
        unit_factor = 1609.34
    elif distance_unit in ["km","kilometer","kilometers"]:
        unit_factor = 1000.0
    elif distance_unit in ["m", "meter", "meters"]:
        unit_factor = 1.0
    return unit_factor

def get_units(
        distance_unit
):
    """ 
    Get plotting labels for the units of distance.
    
    Parameters
    ----------
        distance_unit: str
            unit of distances

    Returns
    -------
        distance_unit: str
            plotting distance label
            
    """
    if distance_unit in ["mi","mile","miles"]:
        distance_unit = "mi"
    elif distance_unit in ["km","kilometer","kilometers"]:
        distance_unit = "km"
    elif distance_unit in ["m", "meter", "meters"]:
        distance_unit = "m"
    return distance_unit

def format_date_string(
        date
    ):
    """ 
    Get plotting representation for the date
    
    Parameters
    ----------
        date: str
            A date

    Returns
    -------
        date: str
            plotting date

    """
    day_num = date.strftime('%d')
    month_num = date.strftime('%m')
    month_str = date.strftime('%B')
    year = date.strftime('%Y')
    
    if day_num[0] == 0:
        day_num = day_num[1:]
    
    if day_num[-1] == "1":
        super_str = "st"
    elif day_num[-1] == "2":
        super_str = "nd"
    elif day_num[-1] == "3":
        super_str = "rd"
    else:
        super_str = "th"
        
    return f"{day_num}{super_str} {month_str} {year}"

def calculate_distance(coords_1, coords_2):
    """ 
    Calculate the geodesic distance between two coordinates
    
    Parameters
    ----------
        coords_1: coordinates class
            First coordinate class
        coords_2: coordinates class
            Second coordinate class

    Returns
    -------
        D: float
            distance between coordinates in miles
    """
    D = geopy.distance.distance([coords_1.long,coords_1.lat],[coords_2.long,coords_2.lat]).miles
    return D

def latlong_to_proj(crs, long,lat):
    """ 
    Convert lat long coordinates into coordinates in new projection
    
    Parameters
    ----------
        crs: str
            coordinate reference system
        lat: float
                latitude value
        long: float
            longitude value
    
    Returns
    -------
        proj: Proj class instance
            Proj class instance
    
    """
    return Proj(crs)(long,lat)

class Coords:
    def __init__(
        self,
        lat = 0,
        long = 0
    ):
        """ 
        Class defining a set of coordinates
        
        Parameters
        ----------
            lat: float
                latitude value
            long: float
                longitude value
        """
        self.lat = lat
        self.long = long
        
        x1,y1 = latlong_to_proj("EPSG:3857", long, lat) #Into Mercator
        self.x = x1
        self.y = y1
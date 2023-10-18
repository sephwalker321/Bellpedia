
from pathlib import Path
import os

import numpy as np
import pandas as pd
import re
import pickle

from bellpedia.functions import load_yaml
from bellpedia.world import World, Tower, Bell
from bellpedia.functions import Coords

class Generate_Config:
    def __init__(
        self, 
    ):
        """ 
        Class of configuration settings used across the module.
        
        Parameters
        ----------
        
        """        
        self.set_fixed()
        self.load_config()
        
    def set_fixed(self):
        """ 
        Set the default fixed configuration parameters.
        
        Parameters
        ----------

        Returns
        -------

        """
        self.working_dir = Path(os.getcwd()).parent

        self.crs_IN   = "EPSG:4326"
        self.crs_OUT  = "EPSG:3857"
        return

    def load_config(self):
        """ 
        Set the customisable configuration parameters.
        
        Parameters
        ----------

        Returns
        -------

        """
        yaml_in = load_yaml(f"{self.working_dir}/bellpedia/config.yaml")
        self.data_dir      = yaml_in["data_folder"]
        self.user_data_dir = yaml_in["user_data_folder"]
        self.plot_dir      = yaml_in["plots_folder"]

        self.distance_unit = yaml_in["distance_unit"]

        #Plotting formating
        self.dpi              = yaml_in["dpi"]
        
        #Dove data settings
        self.ring_type = yaml_in["ring_type"]
        self.dove_refresh = yaml_in["dove_data_refresh"]
        return

    def change_dir(
            self,
            user_dir_new=None,
        ):
        """ 
        Change the road and place directorys from the default.
        TODO Check directory exists?
        
        Parameters
        ----------
            user_dir_new: str
                folder path containing excel list of bell towers
        
        Returns
        -------

        """
        if user_dir_new is not None:
            self.user_data_dir = user_dir_new
        return

    def printout(self):
        """ 
        Print out summary of configuration set up
        TODO Write function
        
        Parameters
        ----------

        Returns
        -------

        """
        return
    
class Generate_World:
    def __init__(
        self, 
        config = Generate_Config(),
    ):
        """ 
        Generate class instance of the world containing Towers and their Bells.
        
        Parameters
        ----------
            config:  class of configuration settings
                 Class of configuration settings used across the module.
            
        """
        self.config = config
        self.dove_dir = f"{self.config.working_dir}/{self.config.data_dir}/dove_data/"
        self.plk_dir = f"{self.config.working_dir}/{self.config.data_dir}/world/"

        filename = "Bellpedia_All.plk"
        if self.config.dove_refresh:
            self.towers = self.create_world_from_dove()
            self.pickle_saver(self.towers, filename)
        else:
            self.towers =  self.create_world_from_pickle(filename)
        self.world = World(self.towers)
        
    def pickle_saver(self, obj, filename):
        """ 
        Save class instance of world to file. 
        
        Parameters
        ----------
            obj: any
                Class to pickle save
            filename: str
                Filename of saved pickle

        Returns
        -------

        """
        with open(self.plk_dir + filename, 'wb') as outp:  # Overwrites any existing file.
            pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)
        return

    def pickle_loader(self, filename):
        """ 
        Load world from pickled file
        
        Parameters
        ----------
            filename: str
                Filename of saved pickle

        Returns
        -------
            world: class instance of the world
                class instance of the world containing Towers and their Bells.

        """
        with open(self.plk_dir + filename, "rb") as f:
            return pickle.load(f)

    def sort_out_type(self, input_value, required_type, default_value):
        """ 
        Turn input value into required type.
        
        Parameters
        ----------
            input_value: any
                The input value to be reformatted
            required_type: type
                The required type of the variable
            default_value: any
                A default value if input_value is nan or None

        Returns
        -------
            output_value: required_type
                The output value of correct type

        """
        if isinstance(input_value, float) or isinstance(input_value, int):
            if required_type == "float":
                if np.isnan(input_value):
                    return default_value
                else:
                    return float(input_value)

            if required_type == "str":
                if np.isnan(input_value):
                    return default_value
                else:
                    return str(input_value)

        elif isinstance(input_value, str):
            if required_type == "float":
                if input_value.isnumeric() == False:
                    return default_value

            if required_type == "str":
                return input_value
        
        return input_value

    def sort_out_bell(self, input_value):
        """ 
        Format the bell number from the string in Dove data. e.g. for chimes, flats and sharps.
        
        Parameters
        ----------
            input_value: str
                Dove bell number

        Returns
        -------
            N: str
                Bell number
            C: str
                Chime number

        """
        N = None
        C = None

        if re.fullmatch("\d+", input_value):
            #Match just a number
            N = int(input_value) 

        elif re.fullmatch("\d+[c]\d+", input_value):
            #Match XcY X Bell, but Chime Y
            N = re.split("c", input_value)[0] 
            C = re.split("c", input_value)[1] 
        elif re.fullmatch("[c]\d+", input_value):
            C = re.split("c", input_value)[1] 
        elif re.fullmatch("[c]\d+[b]", input_value):
            #Match Flat chime
            C = re.split("c", input_value)[1] 
        elif re.fullmatch("[c]\d+[#]", input_value):
            #Match sharp chime
            C = re.split("c", input_value)[1] 
        elif re.fullmatch("[A-Za-z]+", input_value):
            #Match Just a name.
            N = input_value

        elif re.fullmatch("\d+[b][c]\d+", input_value):
            #Match XcY X Bell, but Chime Y
            N = re.split("c", input_value)[0]
            C = re.split("c", input_value)[1] 
        elif re.fullmatch("\d+[#][c]\d+", input_value):
            #Match XcY X Bell, but Chime Y
            N = re.split("c", input_value)[0]
            C = re.split("c", input_value)[1] 

        elif re.fullmatch("\d+[b]", input_value):
            #Match Flat 
            V = re.split("b", input_value)[0]
            N = f"{V}b"
        elif re.fullmatch("\d+[#]", input_value):
            #Match Sharp
            V = re.split("#", input_value)[0]
            N = f"{V}#"
        else:
            print(f"BellNum ERROR: {input_value}")
            N = "Extra"
        return N, C

    def sort_out_dated(self, input_value):
        """ 
        Format the date of bell founding from Dove data
        
        Parameters
        ----------
            input_value: str
                dove founding date

        Returns
        -------
            Date: int
                Year of bell founding

        """
        Date = None

        if re.fullmatch("\d+", input_value):
            #Match just a number
            Date= int(input_value) 
        elif re.fullmatch("[c]\d+", input_value):
            #Match sharp chime
            Date = int(re.split("c", input_value)[1])
        elif re.fullmatch("\\(\d+\\)", input_value):
            #Match sharp chime
            Date = int(input_value.split("(")[1].split(")")[0])
        elif input_value == "nan" or input_value == "(n/d)":
            Date = np.nan
        else:
            print(f"Date ERROR: {input_value}")
            Date = np.nan
        return Date

    def make_tower_from_data(self, dat):
        """ 
        Create individual tower class instance from Dove data
        
        Parameters
        ----------
            dat: pd.dataframe
                Tower data from dove data.

        Returns
        -------
            Tower: Tower Class instance
                A bell tower class instance

        """
        if dat.RingType.lower() != self.config.ring_type:
            return None

        name = dat.Dedicn
        place = dat.Place
        dove_id = dat.TowerID
        bells = []
        coordinates = Coords(dat.Lat, dat.Long)
        postcode = dat.Postcode
        grid_reference=dat.NG
        country = dat.Country
        county = dat.County
        diocese= dat.Diocese
        affiliation = dat.Affiliations
        frames = []
        practice = dat.Practice
        LGrade = dat.LGrade

        name = name
        place = place
        dove_id = dove_id
        bells = bells
        coordinates = coordinates
        postcode = self.sort_out_type(postcode,"str","")
        grid_reference= grid_reference
        country = self.sort_out_type(country,"str","")
        county = self.sort_out_type(county,"str", "")
        diocese = diocese
        affiliation = affiliation
        frames = frames
        practice = practice
        LGrade = LGrade
        
        return Tower(
            name = name,
            place = place,
            dove_id = dove_id,
            bells = bells,
            coordinates = coordinates,
            postcode = postcode,
            grid_reference= grid_reference,
            country = country,
            county = county,
            diocese = diocese,
            affiliation = affiliation,
            frames = frames,
            practice = practice,
            LGrade = LGrade
        )

    def make_bells_from_data(self, dat):
        """ 
        Create list of bell class instance from Dove data for a tower
        
        Parameters
        ----------
            dat: pd.dataframe
                bell data from dove data.

        Returns
        -------
            bells: list
                A list of bell class instances for a single tower

        """
        bells = []
        for Bi in range(len(dat)):
            bell_i = dat.iloc[Bi]
            
            N = bell_i["Bell Role"]
            dove_id = bell_i["Bell ID"]
            note = bell_i["Note"]
            nominal = bell_i["Nominal (Hz)"]
            weight = bell_i["Weight (lbs)"]
            diameter= bell_i["Diameter (in)"]
            caster = bell_i["Caster"]
            founder = bell_i["Founder"]
            dated = bell_i["Cast Date"]
            collection_type = bell_i["Collection Type"]
            listed = bell_i["Listed"]
            canons = bell_i["Canons"]
            turnings = bell_i["Turnings"]
            cracked = bell_i["Cracked"]
            frame_id = bell_i["Frame ID"]

            if collection_type.lower() != self.config.ring_type:
                continue

            N, C = self.sort_out_bell(str(N))
            dove_id = int(dove_id)
            note = note
            nominal = float(nominal)
            weight = weight
            diameter = float(diameter)
            caster = caster
            founder = founder
            dated = self.sort_out_dated(str(dated))
            collection_type = collection_type.lower()
            listed = listed
            canons = canons
            turnings = turnings
            cracked = cracked
            frame_id = frame_id

            bells.append(
                Bell(
                    N = N,
                    C = C,
                    dove_id = dove_id,
                    note = note,
                    nominal = nominal,
                    weight = weight,
                    diameter= diameter,
                    caster = caster,
                    founder = founder,
                    dated = dated,
                    collection_type = collection_type,
                    listed = listed,
                    canons = canons,
                    turnings = turnings,
                    cracked = cracked,
                    frame_id = frame_id
                )
            )
        return bells

    def create_world_from_dove(self):
        """ 
        Create the world from dove data combining all the bells and tower class instances
        
        Parameters
        ----------

        Returns
        -------
            Towers: list
                List of class towers in the world

        """
        Towers_data = pd.read_csv(self.dove_dir + "towers.csv")
        Bells_data = pd.read_csv(self.dove_dir + "bells.csv")
        
        Towers = []
        dove_ids = []
        Markers = list(np.linspace(0, len(Towers_data)+1, 11, dtype=int))
        mark = 10
        print(f"{0} %")
        for Ti in range(len(Towers_data)):
            if Ti+1 in Markers:
                print(f"{mark} %")
                mark += 10
            
            Tower_temp = self.make_tower_from_data(Towers_data.iloc[Ti])
            if Tower_temp is None:
                continue

            Tower_temp.add_bells(self.make_bells_from_data(Bells_data[Bells_data["Tower ID"] == Tower_temp.dove_id]))
            if Tower_temp.dove_id in dove_ids:
                continue

            Towers.append(Tower_temp)  
            dove_ids.append(Tower_temp.dove_id)
                    
        return Towers

    def create_world_from_pickle(self, filename):
        """ 
        Load world from pickled file
        
        Parameters
        ----------
            filename: str
                Filename of saved pickle

        Returns
        -------
            world: class instance of the world
                class instance of the world containing Towers and their Bells.

        """
        return self.pickle_loader(filename)
    
def grab_my_towers(
        filename = 'Examples',
        searchby = "Postcode",
        save = True,
        
        config = Generate_Config(),
    ):
    """ 
    Create world object using user input .xlsx list of towers.
    
    Parameters
    ----------
        filename: str
            Filename of xlsx towers
        searchby: str
            Choices include "name","place","dove_id","Nbells","coordinates","postcode","country" and "county"
        save: bool
            Bool save out .xlsx with more details

    Returns
    -------
        myTowers: world class
            world class instance of user defined towers

    """
    #Consider other search types...
    world = Generate_World().world

    my_list = pd.read_excel(f"{config.working_dir}/{config.user_data_dir}/{filename}.xlsx") 
    my_list["Date"] = my_list["Date"].dt.date
    my_list.sort_values(['Date'], inplace=True, ascending=True) 
    my_list = my_list.drop_duplicates(searchby) 
    my_list_cols = [c for c in my_list.columns if c != 'searchby' if c in ['Date', 'Purpose']]

    myTowers = world.search(searchby, my_list[searchby].values)
    my_list_dove = myTowers.summary

    if searchby != "dove_id":
        my_list_dove.sort_values([searchby], inplace=True, ascending=True) 
    else:
        my_list_dove.sort_index(ascending=True)

    for col in my_list_cols:
        my_list_dove[col] = ""
    if searchby != "dove_id":
        for col in my_list_dove[searchby].values:
            index = my_list_dove[my_list_dove[searchby] == col].index.values
            for i in index:
                my_list_dove.at[i,"Date"] = my_list[my_list[searchby] == col]["Date"].values[0]
                my_list_dove.at[i,"Purpose"] = my_list[my_list[searchby] == col]["Purpose"].values[0]
    else:
        for col in my_list_dove.index.values:
            index = my_list_dove[my_list_dove.index == col].index.values
            for i in index:
                my_list_dove.at[i,"Date"] = my_list[my_list[searchby] == col]["Date"].values[0]
                my_list_dove.at[i,"Purpose"] = my_list[my_list[searchby] == col]["Purpose"].values[0]



    my_list_dove.sort_values(['Date'], inplace=True, ascending=True) 
    if save:
        my_list_dove.to_excel(f"{config.working_dir}/{config.user_data_dir}/{filename}_OUTPUT.xlsx")  
    return myTowers
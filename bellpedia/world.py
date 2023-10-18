import numpy as np
import pandas as pd
import re
import pyaudio
from bellpedia.functions import Coords

cwt2kg = 50.8023
lb2kg = 0.453592
intocm = 2.54

#TODO Get Nearest by Lat Long..?

####################################################################################################
                 ############################ World Class ############################ 
####################################################################################################


class World:
    def __init__(
        self, 
        towers = []
    ):
        """ 
        Create world class instance of the world containing Towers and their Bells.
        
        Parameters
        ----------
            towers: list
                List of towers of tower class

        Returns
        -------

        """
        self.towers = towers
        self.bells = [bell for t in towers for bell in t.bells]

        self.create_lookup()

    @property
    def NTowers(self):
        """ 
        Number of towers in the world
        
        Parameters
        ----------

        Returns
        -------
            Ntowers: int
                Number of towers

        """
        return len(self.towers)

    @property
    def NBells(self):
        """ 
        Number of bells in the world
        
        Parameters
        ----------

        Returns
        -------
            Nbells: int
                Number of bells

        """
        return len(self.bells)

    def search(self, which, search):
        """ 
        Search function to pull towers with quantity 'search' 
        
        Parameters
        ----------
            which: str
                Choices include "name","place","dove_id","Nbells","coordinates","postcode","country" and "county"
            search: str
                Value to find

        Returns
        -------
            world: class instance of the world
                world class instance of the world containing subset of searched Towers and their Bells.
        """
        if type(search) not in [list, np.ndarray]:
            which = which.lower()
            if which == "postcode":
                search = search
            elif which == "nbells" or which == "dove_id":
                search = int(search)
            else:
                search = search.lower()
            search = [search]

        elif type(search) in [list, np.ndarray]:
            search = list(search)

            which = which.lower()
            if which == "postcode":
                search = [s for s in search]
            elif which == "nbells" or which == "dove_id":
                search = [int(s) for s in search]
            else:
                search = [s.lower() for s in search]
                

        indexes = self.lookup[self.lookup[which].isin(search)].index.values
        indexes = list(set(indexes)) #Make sure unique
        return World([self.towers[index] for index in indexes])

    def create_lookup(self):
        """ 
        Create dictionary lookup table in world class
        
        Parameters
        ----------

        Returns
        -------

        """
        dat = {
            "name" : [],
            "place" : [],
            "dove_id" : [],

            "nbells" : [],
            "coordinates" : [],
            "postcode" : [],

            "country" : [],
            "county" : []
        }
        for t in self.towers:
            if t.name is not None:
                dat["name"].append(str(t.name).lower())
            else:
                dat["name"].append(None)

            if t.place is not None:
                dat["place"].append(str(t.place).lower())
            else:
                dat["place"].append(None)

            if t.dove_id is not None:
                dat["dove_id"].append(t.dove_id)
            else:
                dat["dove_id"].append(None)

            if t.Nbells is not None:
                dat["nbells"].append(t.Nbells)
            else:
                dat["nbells"].append(None)

            if t.coordinates is not None:
                dat["coordinates"].append(t.coordinates)
            else:
                dat["coordinates"].append(None)

            if t.postcode is not None:
                dat["postcode"].append(t.postcode)
            else:
                dat["postcode"].append(None)

            if t.country is not None:
                dat["country"].append(str(t.country).lower())
            else:
                dat["country"].append(None)

            if t.county is not None:
                dat["county"].append(str(t.county).lower())
            else:
                dat["county"].append(None)
            
        self.lookup = pd.DataFrame(dat)
        return

    @property
    def summary(self):
        """ 
        Get summary dataframe of world
        
        Parameters
        ----------

        Returns
        -------
            summary: pd.dataframe
                summary of world

        """
        return self.summarytowers

    @property
    def summarytowers(self):
        """ 
        Get summary dataframe of world
        
        Parameters
        ----------

        Returns
        -------
            summary: pd.dataframe
                summary of world

        """
        dfs = []
        for t in self.towers:
            dfs.append(t.summary["Tower"])

        if len(dfs) != 0:
            return pd.concat(dfs)
        else:
            dat = {
                "name" : [],
                "place" : [],
                "dove_id" : [],

                "nbells" : [],
                "coordinates" : [],
                "postcode" : [],

                "country" : [],
                "county" : []
            }
            return pd.DataFrame(dat)
        

    @property
    def summarybells(self):
        """ 
        Get summary dataframe of bells in the world
        
        Parameters
        ----------

        Returns
        -------
            summary: pd.dataframe
                summary of  bells in the world

        """
        dfs = {}

        bi = 0
        for b in self.bells:
            dfs[bi] = b.summary
            bi += 1

        if len(dfs) != 0:
            df = pd.DataFrame(dfs).T
            df = df.set_index("dove_id") 
            df.index.name = None
            df.index = np.array(df.index.values, dtype=np.dtype(int))
            return df
        else:
            dat = {
                "N": [],
                "C": [],
                "Note": [],
                "nominal": [],
                "weight": [],
                "cwt": [],
                "diameter": [],
                "dated" : [],
                "dove_id" : []
            }
            return pd.DataFrame(dat)
        
####################################################################################################
                 ############################ Bell Class ############################ 
####################################################################################################

class Bell:
    def __init__(
        self, 
        N=None,	
        C=None,
        dove_id = None,

        note=None,
        nominal=None,	
        
        weight=None,
        diameter=None,	
        
        caster = None,
        founder=None,

        dated=None,

        collection_type = None,
        listed = None,
        
        canons = None,
        turnings = None,
        cracked = None,

        frame_id = None
    ):
        """ 
        Create bell class instance
        
        Parameters
        ----------
            N: str
                bell number	in tower
            C: str
                chime number in tower
            dove_id: int
                dove tower id number
            note: str
                bell nominal note
            nominal: float
                bell nominal frequency 	
            weight: str
                bell weight in cwt
            diameter: float
                bell diameter in inches	
            caster: str
                casting company of the bell
            founder: str
                founder information of the bell
            dated: str
                date of founding of the bell
            collection_type: str
                #TODO CHECK
            listed: str
                Bell historic listing information
            canons: str
                canon type of the bell
            turnings: str
                #TODO CHECK
            cracked: str
                Is the bell cracked
            frame_id: int
                The dove frame id of the bell frame

        Returns
        -------

        """
        self.N=N
        self.C=C
        self.dove_id = dove_id

        self.note=note
        self.nominal=nominal


        if weight is None or weight == "nan" or (isinstance(weight, str) == False and np.isnan(weight)):
            self.weight = np.nan
            self.kg = np.nan
            self.cwt = np.nan
            self.lb = np.nan
        elif isinstance(weight, str):
            #x-y-z format
            self.weight = weight

            self.cwt = self.StrToCwt(self.weight)
            self.kg = self.cwt*cwt2kg
            self.lb = self.kg / lb2kg
        else:
            #Pounds format
            self.lb = weight
            self.kg = weight*lb2kg
            self.cwt = self.kg / cwt2kg
            self.weight = self.CwtToStr(self.cwt)

        if diameter is None:
            self.diameter = np.nan
        else:
            self.diameter=diameter*intocm

        self.caster = caster
        self.founder = founder

        self.dated=dated

        self.collection_type = collection_type
        self.listed = listed

        self.canons = canons
        self.turnings = turnings
        self.cracked = cracked

        self.frame_id = frame_id

    def StrToCwt(self, string):
        """ 
        Turn string formatted cwt into float
        
        Parameters
        ----------
            string: str
                string formatted cwt

        Returns
        -------
            cwt: float
                cwt of bell

        """
        if len(string) == 0:
            return np.nan
        elif isinstance(string,str):
            D = re.split("-",string)
            return float(D[0])+float(D[1])/4+float(D[2])/112
        else:
            return np.nan

    def CwtToStr(self, cwt):
        """ 
        Turn cwt into string formatted cwt
        
        Parameters
        ----------
            cwt: float
                cwt of bell

        Returns
        -------
            string: str
                string formatted cwt

        """
        int_cwt = (int(cwt))
        quaters = (cwt - int_cwt)*4.0
        int_quarts = (int(quaters))
        lbs = int(np.round((quaters-int_quarts)*28))
        return f"{int_cwt}-{int_quarts}-{lbs}"

    @property
    def chimebell(self, duration=1):
        """ 
        Chime the bell. Produce audio output at the nominal frequency.
        #TODO Make more realistic?
        
        Parameters
        ----------
            duration: float
                Duration in seconds

        Returns
        -------

        """
        p = pyaudio.PyAudio()
        volume = 0.5     # range [0.0, 1.0]
        fs = 44100       # sampling rate, Hz, must be integer
        f = self.nominal      # sine frequency, Hz, may be float
        # generate samples, note conversion to float32 array
        samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
        # for paFloat32 sample values must be in range [-1.0, 1.0]
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=fs,
                        output=True)
        # play. May repeat with different volume values (if done interactively) 
        stream.write(volume*samples)
        stream.stop_stream()
        stream.close()
        p.terminate()
        return

    @property
    def summary(self):
        """ 
        Get summary dataframe of bell
        
        Parameters
        ----------

        Returns
        -------
            summary: pd.dataframe
                summary of  bell

        """
        return {
            "N": self.N, 
            "C": self.C,
            "note": self.note,
            "nominal": self.nominal,
            "weight": self.weight,
            "cwt": self.cwt,
            "diameter": self.diameter,
            "dated" : self.dated,
            "dove_id" : self.dove_id
        }
        
####################################################################################################
                 ############################ Tower Class ############################ 
####################################################################################################


class Tower:
    def __init__(
        self, 
        name = None,
        place = None,
        dove_id = None,

        bells = [],

        coordinates = None,
        postcode = None,
        grid_reference=None,

        country = None,
        county = None,
        diocese = None,
        affiliation = None,

        practice = None,
        LGrade = None,

        frames = []
    ):
        """ 
        Create tower class instance
        
        Parameters
        ----------
            name: str
                Name of bell tower
            place: str
                Town location of bell tower
            dove_id: int
                dove tower id number
            bells: list
                bells class in tower
            coordinates: coords class instance
                coordinates of tower 
            postcode: str
                postcode of tower
            grid_reference: str
                map grid reference of tower
            country: str
                country location of tower 
            county: str
                county location of tower
            diocese: str
                associated diocese of tower
            affiliation: str
                tower affiliation
            practice: str
                tower practice information
            LGrade: str
                tower listed grade information
            frames: list
                list of frames in tower
        Returns
        -------

        """
        self.name = name
        self.place = place
        self.dove_id = dove_id

        self.bells = bells  

        self.coordinates = coordinates 
        self.postcode = postcode 
        self.grid_reference = grid_reference

        self.country = country
        self.county = county
        self.diocese = diocese
        self.affiliation = affiliation

        self.practice = practice
        self.LGrade = LGrade
        
        self.frames = frames
        
        
    def add_bell(self, bell):
        """ 
        Add a bell class to the tower
        
        Parameters
        ----------
            bell: Create bell class instance
                bell class instance to be added to tower

        Returns
        -------

        """
        self.bells.append(bell)
        return

    def add_bells(self, bells):
        """ 
        Add list of bells of bell class to the tower
        
        Parameters
        ----------
            bells: list
                list of bell class instances to be added to tower

        Returns
        -------

        """
        for bell in bells:
            self.bells.append(bell)
        return

    def add_bell_byweightnom(self, weights, start_N=1):
        """ 
        Add undefined bells by weight
        
        Parameters
        ----------
            weights: dict
                dict of weights and nominal frequencies
            start_N: int
                starting bell number

        Returns
        -------

        """
        for i in range(len(weights)):
            bell_i = Bell(
                N       = start_N + i,
                weight  = weights[i][0],
                nominal = weights[i][1]
            )
            self.add_bell(bell_i)
        return

    def get_bell(self, Number):
        """ 
        Get Nth bell from tower
        
        Parameters
        ----------
            Number: int
                Required bell number

        Returns
        -------
            bell_i: Bell class instance
                Required bell

        """
        for bell_i in self.bells:
            if bell_i.N == Number:
                return bell_i
            if bell_i == self.bells[-1]:
                print(f"Couldn't find {Number}th bell")
        return

    @property
    def tenor(self):
        """ 
        Get tenor bell from tower
        
        Parameters
        ----------

        Returns
        -------
            bell_t: Bell class instance
                tenor bell

        """
        if len(self.bells) > 0:
            tenor = self.bells[0]
            for bell in self.bells:
                if bell.kg > tenor.kg:
                    tenor = bell
            return tenor
        else:
            return Bell()

    @property
    def treble(self):
        """ 
        Get treble bell from tower
        
        Parameters
        ----------

        Returns
        -------
            bell_t: Bell class instance
                treble bell

        """
        if len(self.bells) > 0:
            treble = self.bells[0]
            for bell in self.bells:
                if bell.kg < treble.kg:
                    treble = bell
            return treble
        else:
            return Bell()

    @property
    def Nbells(self):
        """ 
        Return the number of bells of the tower excluding chimes
        
        Parameters
        ----------

        Returns
        -------
            count: int
                number of bells in the tower

        """
        count = 0
        for bell in self.bells:
            if bell.N is None:
                continue
            
            if re.fullmatch("\d+", str(bell.N)):
                count += 1
        return count
    
    @property
    def NbellsAll(self):
        """ 
        Return the number of bells including the chime of the tower
        
        Parameters
        ----------

        Returns
        -------
            count: int
                number of bells in the tower

        """
        return len([bell.N for bell in self.bells])

    def ring_change(self, sequence=[]):
        """ 
        Ring the change in the tower. Produce audio output at the nominal frequencies.
        #TODO Make more realistic?
        
        Parameters
        ----------
            sequence: list
                integer order of bells

        Returns
        -------

        """
        if len(sequence) == 0:
            sequence = [i for i in range(1,self.Nbells+1)]

        gapsize=0.2 #seconds
        for place in sequence:
            bell = self.get_bell(place)
            bell.chimebell
        return

    @property
    def summary(self):
        """ 
        Get summary dataframe of the tower
        
        Parameters
        ----------

        Returns
        -------
            summary: pd.dataframe
                summary of the bell tower

        """
        bell_sum = {}
        i = 1
        for bell in self.bells:
            bell_sum[i] = bell.summary
            i += 1


        tower_sum = {
            "Name" : [self.name],
            "Place" : [self.place],
            "Bells" : [self.Nbells],

            "Tenor" : [self.tenor.weight],
            "Hundredweight" : [self.tenor.cwt],
            "Country" : [self.country],
            "County" : [self.county],
            "Postcode" : [self.postcode]
        }

        df_bell = pd.DataFrame(bell_sum).T
        if df_bell.shape[0] > 0:
            df_bell = df_bell.sort_values(by=["N", 'cwt'])
            df_bell = df_bell.reset_index(drop=True)
            df_bell = df_bell.set_index("dove_id")
            df_bell.index.name = None
        df_tower = pd.DataFrame(tower_sum, index=[self.dove_id])
        return {"Tower" : df_tower, "Bells" : df_bell}
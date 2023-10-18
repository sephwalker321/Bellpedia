from tkinter.tix import COLUMN
from bellpedia.plots_format import fig_initialize, set_size
fig_initialize()


from bellpedia.functions import latlong_to_proj, calculate_distance
from bellpedia.load import Generate_Config
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import contextily as ctx
import os

from bellpedia.world import World

class Geoplots:
    def __init__(
        self,
        config = Generate_Config(),
        region = "UK",
        fileprefix="",
        imformat="pdf",
    ):
        """ 
        Plotting class instance
        
        Parameters
        ----------
            config: class of configuration settings
                Class of configuration settings used across the module.
            region: str
                region for lat long limits on plots. Choices include 'Channel Islands','Isle of Man', 'Netherlands', 'Belgium', 'Spain', 'Grenada', 'France', 'England', 'Scotland', 'Wales', 'Northern Ireland', 'Republic of Ireland', 'Kenya', 'Zimbabwe', 'South Africa', 'India', 'Pakistan', 'Singapore','St Vincent', 'Australia', 'New Zealand'
            fileprefix: str
                prefix for filenames for plots
            imformat: str
                format of saved figures e.g. 'pdf'

        """
        self.config = config
        self.imformat = imformat
        
        self.region = region
        self.set_filepath(fileprefix=fileprefix)

        self.source = ctx.providers.OpenStreetMap.Mapnik
        self.cmap = plt.get_cmap('hsv')
        self.minbells = 1
        self.maxbells = 16
        
    def set_filepath(self, fileprefix):
        """ 
        Set the plot directories
        
        Parameters
        ----------
            fileprefix: str
                prefix for filenames for plots

        Returns
        -------

        """
        #Make plot directory
        plot_dir = f"{self.config.working_dir}/{self.config.plot_dir}"
        if os.path.exists(plot_dir) == False:
            os.mkdir(plot_dir)
            
        if fileprefix != "":
            self.filepath = f"{plot_dir}/{fileprefix}_"
        else:
            self.filepath = f"{plot_dir}/"
        return
        
    def restrict_plot(self,place):
        """ 
        Get the lat long plot restrictions for geoplot.
        
        Parameters
        ----------
            place: str
                region for lat long limits on plots. Choices include 'Channel Islands','Isle of Man', 'Netherlands', 'Belgium', 'Spain', 'Grenada', 'France', 'England', 'Scotland', 'Wales', 'Northern Ireland', 'Republic of Ireland', 'Kenya', 'Zimbabwe', 'South Africa', 'India', 'Pakistan', 'Singapore','St Vincent', 'Australia', 'New Zealand'
            
        Returns
        -------
            xlim: np.array
                Longitude xlimit
            ylim: np.array
                Latitude ylimit
            zoom: int
                Resolution of open source map
        """
        if place in ['Channel Islands', "England","Scotland", "Wales", "Northern Ireland","Republic of Ireland", 'Isle of Man', "UK"]:
            xlim = [-11.2,2.5]
            ylim = [49.5,59]
            return np.array(xlim), np.array(ylim), 8

        elif place in ["Canada", 'United States of America']:
            xlim = [-125,-65]
            ylim = [20,80]
            return np.array(xlim), np.array(ylim), 1

        elif place in ['Channel Islands','Isle of Man', 'Netherlands', 'Belgium', 'Spain', 'Grenada', 'France', 'England', 'Scotland', 'Wales', 'Northern Ireland', 'Republic of Ireland']:
            xlim = [-14.238281,16.611328]
            ylim = [35.940866,59.083277]
            return np.array(xlim), np.array(ylim), 1
            
        elif place in ['Kenya', 'Zimbabwe', 'South Africa']:
            xlim = [4.710925,46.722643]
            ylim = [-35.734913,4.603028]
            return np.array(xlim), np.array(ylim), 1

        elif place in ['India', 'Pakistan', 'Singapore']:
            xlim = [57.796873,107.367185]
            ylim = [0.246806,35.963483]
            return np.array(xlim), np.array(ylim), 1

        elif place in ['St Vincent', 'Australia', 'New Zealand']:
            xlim = [111.076172,179.999]
            ylim = [-47.773102,-11.355495]
            return np.array(xlim), np.array(ylim), 1
            
        return np.array([-180,180]), np.array([-80,80]), 1

    def make_all_plots(
            self, 
            world, 
            fileprefix="",
            region="England",
            plot_Locations=True,
            plot_NBells=True,
            plot_TenorWeight=True,
            plot_Freq=True,
            plot_Weight=True,
            plot_Diameter=True,
            plot_Dated=True,
            ):
        """ 
        Make all the plots.
        
        Parameters
        ----------
            world: class instance of the world
                class instance of the world containing Towers and their Bells.
            fileprefix: str
                prefix for filenames for plots
            place: str
                region for lat long limits on plots. Choices include 'Channel Islands','Isle of Man', 'Netherlands', 'Belgium', 'Spain', 'Grenada', 'France', 'England', 'Scotland', 'Wales', 'Northern Ireland', 'Republic of Ireland', 'Kenya', 'Zimbabwe', 'South Africa', 'India', 'Pakistan', 'Singapore','St Vincent', 'Australia', 'New Zealand'
            plot_Locations: bool
                Scatter plot of bell tower locations
            plot_NBells: bool
                Histogram of the number of bells per tower 
            plot_TenorWeight: bool
                Histogram of tenor weight 
            plot_Freq: bool
                Histogram of nominal bell frequencies
            plot_Weight: bool
                Histogram of bell weights
            plot_Diameter: bool
                Histogram of bell diameters 
            plot_Dated: bool
                Histogram of the dates of bell foundings
                
        Returns
        -------
           
        """
        self.set_filepath(fileprefix)
        self.region = region
        
        if plot_Locations:
            self.plot_locations(world)
        if plot_NBells:
            self.histo_nbells(world)
        if plot_TenorWeight:
            self.histo_tenor_weight(world)
        if plot_Freq:
            self.histo_nominal(world)
        if plot_Weight:
            self.histo_bells_weight(world)
        if plot_Diameter:
            self.histo_bells_diameter(world)
        if plot_Dated:
            self.histo_bells_date(world)

    def plot_locations(self, world):
        """ 
        Scatter plot of bell tower locations
        
        Parameters
        ----------
            world: class instance of the world
                class instance of the world containing Towers and their Bells.

        Returns
        -------

        """
        cs = self.cmap(np.linspace(0.12, 1, self.maxbells))
        if type(world).__name__ == "World":
            pass
        elif type(world).__name__ == "Tower":
            world = World([world])

        xlim, ylim, zoom = self.restrict_plot(self.region)
        x1,y1 = latlong_to_proj(self.config.crs_OUT, xlim[0],ylim[0])
        x2,y2 = latlong_to_proj(self.config.crs_OUT, xlim[1],ylim[1])

        f, ax = plt.subplots(1,1, figsize=(8.27, 11.69))
        ax.axis('off')

        for t in world.towers:
            ax.scatter(
                x=t.coordinates.x,y=t.coordinates.y, color=cs[t.Nbells-1], 
                alpha=.4, marker="X",edgecolors='black',
            )

        for c in range(self.minbells, self.maxbells+1):
            ax.scatter(
                x=-np.inf, y=-np.inf, color=cs[c-1],
                label=f"{c} bells", 
                marker="X",edgecolors='black',
            )
        ax.legend()
        ax.set_ylim([y1,y2])
        ax.set_xlim([x1,x2])
        ctx.add_basemap(ax=ax, crs=self.config.crs_OUT, zoom=zoom,source=self.source)
        plt.savefig(f"{self.filepath}TowerLocations.{self.imformat}", format=self.imformat, dpi=self.config.dpi)
        plt.show()
        return
        
    def histo_nbells(self, world):
        """ 
        Histogram of the number of bells per tower
        
        Parameters
        ----------
            world: class instance of the world
                class instance of the world containing Towers and their Bells.

        Returns
        -------

        """
        df = world.summary

        bins = np.arange(self.minbells, self.maxbells+1.5, 1)-0.5
        xs = (bins[1:]+bins[:-1])/2
        hist, _ = np.histogram(df["Bells"].values, bins=bins)

        f, ax = plt.subplots(1,1, figsize=set_size())
        ax.bar(xs, hist, width=1, align="center")
        ax.set_xlim([0-0.5, self.maxbells+0.5])
        ax.set_xlabel("Number of bells")
        ax.set_ylabel("Number of towers")
        plt.savefig(f"{self.filepath}TowerNBells.{self.imformat}", format=self.imformat, dpi=self.config.dpi)
        plt.show()
        return

    def histo_tenor_weight(self, world):
        """ 
        Histogram of tenor weight
        
        Parameters
        ----------
            world: class instance of the world
                class instance of the world containing Towers and their Bells.

        Returns
        -------

        """
        df = world.summary

        Max = int(np.nanmax(df["Hundredweight"].values))+1
        bins = np.arange(0, Max, 1)

        xs = (bins[1:]+bins[:-1])/2
        hist, _ = np.histogram(df["Hundredweight"].values, bins=bins)

        f, ax = plt.subplots(1,1, figsize=set_size())
        ax.bar(xs, hist, width=xs[1]-xs[0], align="center")
        ax.set_xlim([0, Max])
        ax.set_xlabel("Tenor weight (cwt)")
        ax.set_ylabel("Number of towers")
        plt.savefig(f"{self.filepath}TowerWeight.{self.imformat}", format=self.imformat, dpi=self.config.dpi)
        plt.show()
        return

    def histo_nominal(self, world):
        """ 
        Histogram of nominal bell frequencies
        
        Parameters
        ----------
            world: class instance of the world
                class instance of the world containing Towers and their Bells.

        Returns
        -------

        """
        df = world.summarybells

        Min = 100
        Max = 10000
        bins = np.logspace(np.log10(Min), np.log10(Max), 100)
        xs = (bins[1:]+bins[:-1])/2
        hist, _ = np.histogram(df["nominal"].values, bins=bins)

        f, ax = plt.subplots(1,1, figsize=set_size())
        ax.bar(bins[:-1], hist, width=bins[1:]-bins[:-1], align="edge")
        ax.set_xlim([Min, Max])
        ax.set_xlabel("Frequency of bell (Hz)")
        ax.set_ylabel("Number of bells")
        ax.set_xscale("log")
        plt.savefig(f"{self.filepath}BellsFreq.{self.imformat}", format=self.imformat, dpi=self.config.dpi)
        plt.show()
        return

    def histo_bells_weight(self, world):
        """ 
        Histogram of bell weights
        
        Parameters
        ----------
            world: class instance of the world
                class instance of the world containing Towers and their Bells.

        Returns
        -------

        """
        df = world.summarybells

        Max = int(np.nanmax(df["cwt"].values))+1
        bins = np.arange(0, Max, 0.25)


        xs = (bins[1:]+bins[:-1])/2
        hist, _ = np.histogram(df["cwt"].values, bins=bins)

        f, ax = plt.subplots(1,1, figsize=set_size())
        ax.bar(xs, hist, width=xs[1]-xs[0], align="center")
        ax.set_xlim([0, Max])
        ax.set_xlabel("Bell weight (cwt)")
        ax.set_ylabel("Number of bells")
        plt.savefig(f"{self.filepath}BellsWeight.{self.imformat}", format=self.imformat, dpi=self.config.dpi)
        plt.show()
        return
    
    def histo_bells_diameter(self, world):
        """ 
        Histogram of bell diameters
        
        Parameters
        ----------
            world: class instance of the world
                class instance of the world containing Towers and their Bells.

        Returns
        -------

        """
        df = world.summarybells

        Max = int(np.nanmax(df["diameter"].values))+1

        bins = np.linspace(0, Max, 100)
        xs = (bins[1:]+bins[:-1])/2
        hist, _ = np.histogram(df["diameter"].values, bins=bins)
        f, ax = plt.subplots(1,1, figsize=set_size())
        ax.bar(xs, hist, width=xs[1]-xs[0], align="center")
        ax.set_xlim([0, Max])
        ax.set_xlabel("Diameter of bell (cm)")
        ax.set_ylabel("Number of bells")
        plt.savefig(f"{self.filepath}BellsDiameter.{self.imformat}", format=self.imformat, dpi=self.config.dpi)
        plt.show()
        return
    
    def histo_bells_date(self, world):
        """ 
        Histogram of the dates of bell foundings
        
        Parameters
        ----------
            world: class instance of the world
                class instance of the world containing Towers and their Bells.

        Returns
        -------

        """
        df = world.summarybells

        Min = 1500
        Max = 2100

        bins = np.arange(Min, Max, 10)
        xs = (bins[1:]+bins[:-1])/2
        hist, _ = np.histogram(df["dated"].values, bins=bins)
        f, ax = plt.subplots(1,1, figsize=set_size())
        ax.bar(xs, hist, width=xs[1]-xs[0], align="center")
        ax.set_xlim([Min, Max])
        ax.set_xlabel("Year of bell founding")
        ax.set_ylabel("Number of bells")
        plt.savefig(f"{self.filepath}BellsDated.{self.imformat}", format=self.imformat, dpi=self.config.dpi)
        plt.show()
        return
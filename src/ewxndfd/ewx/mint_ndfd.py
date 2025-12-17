from ewxndfd.ewx.ewx_ndfd_file import NDFD, DEFAULT_TIME_ZONE

class NDFDMinT(NDFD):
    """small class for reading, filtering, and transforming NDFD
    daily minimum temperature forecast csv data files
    """
    
    def __init__(self, ndfd_dir:str, tz:str=DEFAULT_TIME_ZONE):
        """initialize NDFDmint object

        Args:
            path (str): base path where NDFD files are found
            tz (str): timezone string for local time zone
        """
        super().__init__(ndfd_dir, "mint", "Celsius", "°C", tz)
    
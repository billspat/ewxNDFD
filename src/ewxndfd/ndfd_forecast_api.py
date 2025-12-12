"""methods to get unsummarized/ detailed forecast from the NDFD XML api and 
summarize by day
"""

import requests
import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import sys
from datetime import date # , timedelta, datetime



DEFAULT_USER_AGENT = '(enviroweather.msu.edu, ewx@enviroweather.msu.edu)'
# for testing
LANSING_LAT_LON = (42.73, -84.55)  # approximate lat/lon for Lansing, MI



def construct_ndfd_digital_forecast_url(lat, lon, begin=None, end=None):
    # dwml by default, not summarized 
    base_url = "https://digital.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php"
    
    if begin is None:
        date_today =  date.today().isoformat() + "T00:00:00"
    else:
        date_today = begin
        
    if end is None:
        date_future = '2030-04-20T00:00:00'
    else:
        date_future = end
        
    forecast_params = f"Unit=m&lat={lat}&lon={lon}&product=time-series&begin={date_today}&end={date_future}&maxt=maxt&mint=mint&rh=rh&wspd=wspd&qpf=qpf"
    
    forecast_url = f"{base_url}?{forecast_params}"
    
    return forecast_url

def request_ndfd_digital_forecast(lat, lon, user_agent = DEFAULT_USER_AGENT):
    
    # dwml by default, not summarized 
    # base_url = "https://digital.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php?Unit=m"
    
    date_today =  date.today().isoformat() + "T00:00:00"
    date_future = '2030-04-20T00:00:00'
    
    
    # forecast_params = f"&lat={lat}&lon={lon}&product=time-series&begin={date_today}&end={date_future}&maxt=maxt&mint=mint&rh=rh&wspd=wspd&qpf=qpf"
    
    # forecast_elements = "maxt=maxt&mint=mint&rh=rh&wsp=wspd&qpf=qpf&appt=appt" 
    # base_url = "https://digital.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php?"
    # forecast_url = f"{base_url}?lat={lat}&lon={lon}&product=time-series&{forecast_elements}"  #&begin={begin}&end={end}
     
    forecast_url = construct_ndfd_digital_forecast_url(lat, lon, begin=date_today, end=date_future) # f"{base_url}?{forecast_params}"
    

    headers = {"User-Agent": user_agent}
    
    forecast_response = requests.get(forecast_url, headers=headers)
    return(forecast_response)
    
  

def get_start_times(root, time_layout_key):
    time_layouts = root.findall('.//time-layout')
    for tl in time_layouts:
        layout_key = tl.find('layout-key').text
        if layout_key == time_layout_key:
            start_times = [st.text for st in tl.findall('start-valid-time')]
            return start_times
    return []


def weather_metric_xml_to_df(root, metric_path):
    weather_values = root.find(metric_path)
    time_layout_key = weather_values.get('time-layout')
    start_times = get_start_times(root, time_layout_key)
    values = [v.text for v in weather_values.findall('value')]
    
    df = pd.DataFrame(
        {
            'forecast_time': start_times,
            'value': values
        }
    )
    df['forecast_date'] = pd.to_datetime(df['forecast_time']).dt.date
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df

def weather_metric_name_from_xml(root, metric_path):
    weather_values = root.find(metric_path)
    unit_name = weather_values.get('units')
    value_name = weather_values.find('name').text
    return f"{value_name} ({unit_name})"
    
    
def daily_forecast_summary(lat, lon, hourly_weather = None):
    ######
    # add hourly weather into df here for today
    # the way it's added depends on the metric and how that's stored in df from the xml
    resp = request_ndfd_digital_forecast(lat, lon)
    # if resp has an error # note status code is always 200 even if params are invalid
    if "ERROR" in resp.text.upper():
        # extract error message from resp.text and put in raise msg
        print(resp.text)
        raise ValueError("Error retrieving NDFD digital weather data.")
        
        
    root = ET.fromstring(resp.text)
    
    
    metric_path = './/humidity'
    metric_name = weather_metric_name_from_xml(root, metric_path)
    humidity_df = weather_metric_xml_to_df(root, metric_path)
    # humidity must be summarized 
    humidity_daily = pd.DataFrame(
        { 
            f'Maximum {metric_name}': humidity_df.groupby('forecast_date')['value'].max(), 
            f'Minimum {metric_name}': humidity_df.groupby('forecast_date')['value'].min()
        }
    )
    
    
    metric_path = ".//temperature[@type='minimum']"
    metric_name = weather_metric_name_from_xml(root, metric_path)
    min_temperature_df = weather_metric_xml_to_df(root, metric_path)
    min_temperature_daily = pd.DataFrame(
        { 
            f'{metric_name}': min_temperature_df.groupby('forecast_date')['value'].first()
        }
    )
    
    metric_path = ".//temperature[@type='maximum']"
    metric_name = weather_metric_name_from_xml(root, metric_path)
    max_temperature_df = weather_metric_xml_to_df(root, metric_path)
    max_temperature_daily = pd.DataFrame(
        { 
            f'{metric_name}': max_temperature_df.groupby('forecast_date')['value'].first()  
        }
    )
    
    summary_df = pd.concat([humidity_daily, min_temperature_daily, max_temperature_daily], axis=1)
    summary_df = summary_df.rename_axis('forecast_date').reset_index()

    return summary_df

def main():
    def _valid_lat(value: str) -> float:
        try:
            v = float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"latitude must be a float: {value}")
        if v < -90.0 or v > 90.0:
            raise argparse.ArgumentTypeError(f"latitude out of range [-90, 90]: {v}")
        return v

    def _valid_lon(value: str) -> float:
        try:
            v = float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"longitude must be a float: {value}")
        if v < -180.0 or v > 180.0:
            raise argparse.ArgumentTypeError(f"longitude out of range [-180, 180]: {v}")
        return v

    parser = argparse.ArgumentParser(
        prog="ndfd_forecast_api",
        description="Retrieve and summarize NDFD digital weather forecast for a location",
    )

    parser.add_argument("--latitude", "-lat", type=_valid_lat,
                        help="Latitude in decimal degrees (-90..90). If omitted, a default will be used.")
    parser.add_argument("--longitude", "-lon", type=_valid_lon,
                        help="Longitude in decimal degrees (-180..180). If omitted, a default will be used.")
    parser.add_argument("--user-agent", dest="user_agent", default=DEFAULT_USER_AGENT,
                        help="User-Agent header to send with requests")

    args = parser.parse_args()

    # Use provided values or fall back to default
    lat = args.latitude if args.latitude is not None else LANSING_LAT_LON[0]
    lon = args.longitude if args.longitude is not None else LANSING_LAT_LON[1]

    try:
        daily_forecast_df = daily_forecast_summary(lat, lon, hourly_weather=None)
    except Exception as exc:
        print(f"Error retrieving forecast: {exc}", file=sys.stderr)
        sys.exit(2)

    # print CSV to stdout
    print(daily_forecast_df.to_csv(index=True))
    
if __name__ == "__main__":
    main()

    
    
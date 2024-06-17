import pandas as pd
import datetime
import requests

def day_offset(start, end, offset):
    current = [start]
    while max(current) < end:
        if(max(current) + datetime.timedelta(days= offset) < end):
            current.append(max(current) + datetime.timedelta(days= offset))
        else:
           current.append(end) 
           
    return current

def hour_offset(start, end, offset):
    current = [start]
    while max(current) < end:
        if(max(current) + datetime.timedelta(hours = offset) < end):
            current.append(max(current) + datetime.timedelta(hours = offset))
        else:
           current.append(end) 
           
    return current

def eia_get(api_key, 
            api_path, 
            data = "value", 
            facets = None, 
            start = None, 
            end = None, 
            length = None, 
            offset = None, 
            frequency = None):
    
    class response:
        def __init__(output, data, url, parameters):
            output.data = data
            output.url = url
            output.parameters = parameters
    
    if type(api_key) is not str:
        print("Error: The api_key argument is not a valid string")
        return
    elif len(api_key) != 40:
        print("Error: The length of the api_key is not valid, must be 40 characters")
        return
    
    if api_path[-1] != "/":
        api_path = api_path + "/"
    
    if facets is None:
        fc = ""
    else:
        fc = ""
    for i in facets.keys():
        if type(facets[i]) is list:
            for n in facets[i]:
                fc = fc + "&facets[" + i + "][]=" + n
        elif type(facets[i]) is str:
            fc = fc + "&facets[" + i + "][]=" + facets[i]
    
    if start is None:
        s = ""
    else:
        if  type(start) is datetime.date:
            s = "&start=" + start.strftime("%Y-%m-%d")
        elif type(start) is datetime.datetime:
            s = "&start=" + start.strftime("%Y-%m-%dT%H")
        else:
            print("Error: The start argument is not a valid date or time object")
            return
             

    if end is None:
        e = ""
    else:
        if  type(end) is datetime.date:
            e = "&end=" + end.strftime("%Y-%m-%d")
        elif type(end) is datetime.datetime:
            e = "&end=" + end.strftime("%Y-%m-%dT%H")
        else:
            print("Error: The end argument is not a valid date or time object")
            return

    if length is None:
        l = ""
    else:
        l = "&length=" + str(length)

    if offset is None:
        o = ""
    else: 
        o = "&offset=" + str(offset)

    if frequency is None:
        fr = ""
    else:
        fr = "&frequency=" + str(frequency)

    url = "https://api.eia.gov/v2/" + api_path + "?data[]=value" + fc + s + e + l + o + fr          

    
    d = requests.get(url + "&api_key=" + api_key).json()

    df = pd.DataFrame(d['response']['data'])
    # Reformating the output
    df["period"] = pd.to_datetime(df["period"])
    df["value"] = pd.to_numeric(df["value"])
    df = df.sort_values(by = ["period"])

    parameters = {
        "api_path": api_path,
        "data" : data,
        "facets": facets, 
        "start": start, 
        "end": end, 
        "length": length, 
        "offset": offset, 
        "frequency": frequency
    }
    output = response(data = df, url = url + "&api_key=", parameters = parameters)
    return output






def eia_backfill(start, end, offset, api_key, api_path, facets):
    
    class response:
        def __init__(output, data, parameters):
            output.data = data
            output.parameters = parameters
    
    if type(api_key) is not str:
        print("Error: The api_key argument is not a valid string")
        return
    elif len(api_key) != 40:
        print("Error: The length of the api_key is not valid, must be 40 characters")
        return
    
    if api_path[-1] != "/":
        api_path = api_path + "/"    

    if  type(start) is datetime.date:
        s = "&start=" + start.strftime("%Y-%m-%d")
    elif type(start) is datetime.datetime:
        s = "&start=" + start.strftime("%Y-%m-%dT%H")
    else:
        print("Error: The start argument is not a valid date or time object")
        return
             

    if  type(end) is datetime.date:
        e = "&end=" + end.strftime("%Y-%m-%d")
    elif type(end) is datetime.datetime:
        e = "&end=" + end.strftime("%Y-%m-%dT%H")
    else:
        print("Error: The end argument is not a valid date or time object")
        return
    
    if  type(start) is datetime.date:
        time_vec_seq = day_offset(start = start, end = end, offset = offset)
    elif  type(start) is datetime.datetime:
        time_vec_seq = hour_offset(start = start, end = end, offset = offset)

    
    for i in range(len(time_vec_seq[:-1])):
        start = time_vec_seq[i]
        if i < len(time_vec_seq[:-1]) - 1:
            end = time_vec_seq[i + 1] -  datetime.timedelta(hours = 1)
        elif i == len(time_vec_seq[:-1]) - 1:
            end = time_vec_seq[i + 1]
        temp = eia_get(api_key = api_key, 
                       api_path = api_path, 
                       facets= facets, 
                       start = start,
                       data = "value", 
                       end = end)
        if i == 0:
            df = temp.data
        else:
            df = df._append(temp.data)

    parameters = {
        "api_path": api_path,
        "data" : "value",
        "facets": facets, 
        "start": start, 
        "end": end, 
        "length": None, 
        "offset": offset, 
        "frequency":None
    }
    output = response(data = df, parameters = parameters)
    return output

        

def eia_metadata(api_key, api_path = None):
    
    class response:
        def __init__(output, meta, url, parameters):
            output.meta = meta
            output.url = url
            output.parameters = parameters


    if type(api_key) is not str:
        print("Error: The api_key argument is not a valid string")
        return
    elif len(api_key) != 40:
        print("Error: The length of the api_key is not valid, must be 40 characters")
        return
    
    if api_path is None:
        url = "https://api.eia.gov/v2/" + "?api_key="
    else:
        if api_path[-1] != "/":
            api_path = api_path + "/"
        url = "https://api.eia.gov/v2/" + api_path + "?api_key="

    d = requests.get(url + api_key).json()

    parameters = {
        "api_path": api_path
    }

    output = response(url = url, meta = d["response"], parameters= parameters)

    return output 

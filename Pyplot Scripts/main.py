import pandas as pd
import matplotlib.pyplot as plt
import os, glob
import numpy as np
import plot

def import_df(file, timestamps=pd.DataFrame()):
    df = pd.read_csv(file)
    df["Time"] = pd.to_datetime(df["Time"])
    min = df["Time"].min() 
    df["Time"] = df["Time"] - min
    df.interpolate(inplace=True)

    if not timestamps.empty:
        # timestamps["Start Time"] = timestamps["Start Time"] - min
        timestamps = timestamps - min
        return df, timestamps
    return df

def import_timestamps(file):
    series = pd.read_json(file,typ="series")
    df = series.to_frame(name="timestamp") 
    return df

def read_files(dir):
    # geds_files = os.listdir(dir+"\GEDS\\logs-*")
    # base_files = os.listdir(glob.glob(dir+"\Baseline\\logs-*"))
    baseline_files = []
    geds_files = []
    for file in glob.glob(os.path.join(dir+"\\Baseline\\", '*')):
        if os.path.isdir(file):
            baseline_files.append(file+"\\timestamps.json")
        else:
            baseline_files.append(file)
    for file in glob.glob(os.path.join(dir+"\\GEDS\\", '*')):
        if os.path.isdir(file):
            geds_files.append(file+"\\timestamps.json")
        else:
            geds_files.append(file)

    baseline_throughput_file = ""
    baseline_timestamp_file = ""
    geds_throughput_file = ""
    geds_timestamp_file = ""


    for file in baseline_files:
        if "Container Operation Processor Delay Latency" in file:
            baseline_lat = import_df(file)
        elif "Cache Used" in file:
            baseline_cache = import_df(file)
        elif "Write Bytes" in file:
            baseline_throughput_file = file
        elif "Write Latency" in file:
            baseline_write_lat = import_df(file)
        elif ".json" in file:
            baseline_timestamp_file = file
    baseline_throughput, baseline_timestamps = import_df(baseline_throughput_file,import_timestamps(baseline_timestamp_file))

    for file in geds_files:
        if "Container Operation Processor Delay Latency" in file:
            geds_lat = import_df(file)
        elif "Cache Used" in file:
            geds_cache = import_df(file)
        elif "Write Bytes" in file:
            geds_throughput_file = file
        elif "Write Latency" in file:
            geds_write_lat = import_df(file)
        elif ".json" in file:
            geds_timestamp_file = file
    geds_throughput, geds_timestamps = import_df(geds_throughput_file,import_timestamps(geds_timestamp_file))



    geds_lat = import_df(geds_files[0])
    geds_cache = import_df(geds_files[2])
    geds_write_lat = import_df(geds_files[4])
    geds_throughput, geds_timestamps = import_df(geds_files[3],timestamps=import_timestamps(geds_files[1]))

    file_dic = {
    "Baseline": {
        "latency":baseline_lat,
        "timestamps":baseline_timestamps,
        "cache": baseline_cache,
        "throughput": baseline_throughput,
        "write latency": baseline_write_lat
                    },
    "GEDS": {
        "latency":geds_lat,
        "timestamps":geds_timestamps,
        "cache": geds_cache,
        "throughput": geds_throughput,
        "write latency": geds_write_lat
                    }
                }
    return file_dic

if __name__ == "__main__":
    # workingdir = "C:\Users\Omar_Jundi\OneDrive - Dell Technologies\Documents\Projects\Cloudskin\Pravega-GEDS Experiment Data\Exported Grafana Metrics\2024-05-23-1gb-geds-1.5gb-pravega-5-writers_readers"
    workingdir = "Exported Grafana Metrics\\run"
    plot.outputdir = workingdir
    data = read_files(workingdir)

    plot.throughput_lat(data["GEDS"]["throughput"],data["GEDS"]["latency"], data["GEDS"]["timestamps"], geds=True)
    plot.throughput_lat_comparative(data["Baseline"]["throughput"],data["GEDS"]["throughput"],data["Baseline"]["latency"],data["GEDS"]["latency"],data["Baseline"]["timestamps"])

    # GEDS
    plot.cache_use(data["GEDS"]["cache"],data["Baseline"]["timestamps"],geds=True)
    plot.write_latency(data["GEDS"]["write latency"],data["Baseline"]["timestamps"],geds=True)

    # Baseline
    plot.throughput_lat(data["Baseline"]["throughput"], data["GEDS"]["latency"],data["Baseline"]["timestamps"], geds=False)
    plot.cache_use(data["Baseline"]["cache"], data["Baseline"]["timestamps"],geds=False)
    plot.write_latency(data["Baseline"]["write latency"], data["Baseline"]["timestamps"],geds=False)
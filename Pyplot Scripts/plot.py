import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
import os
import json 


global outputdir

global col1
global col2
global ticks_x_throughput
global ticks_x_latency

col1 = "steelblue"
col2 = "orange"

ticks_x_throughput = ticker.FuncFormatter(lambda x, pos: '{0:g} Mbps'.format(x/1e6))
ticks_x_latency = ticker.FuncFormatter(lambda x, pos: '{0:g}s'.format(x/1000))



def throughput_lat_comparative(baseline_throughput, geds_throughput, baseline_lat, geds_lat, timestamps):
    fig, ax = plt.subplots(2,1)
    fig.set_size_inches(18.5,10.5)

    throughput_1 = baseline_throughput["pravega-pravega-segment-store-0"].sum()  / 1e+9
    throughput_2 = geds_throughput["pravega-pravega-segmentstore-0"].sum()  / 1e+9

    if baseline_throughput["pravega-pravega-segment-store-0"].max() > geds_throughput["pravega-pravega-segmentstore-0"].max():
        l1 = baseline_throughput.plot(ax=ax[0], y="pravega-pravega-segment-store-0", x="Time", stacked = False, kind="area",color=col1, label=f"Baseline (Total Data Buffered: {throughput_1:.2f}GB)")
        l2 = geds_throughput.plot(ax=ax[0], y="pravega-pravega-segmentstore-0", x="Time", stacked = False, kind="area",color=col2, label=f"GEDS Integrated  (Total Data Buffered: {throughput_2:.2f}GB)")
    else:
        l2 = geds_throughput.plot(ax=ax[0], y="pravega-pravega-segmentstore-0", x="Time", stacked = False, kind="area",color=col2, label=f"GEDS Integrated  (Total Data Buffered: {throughput_2:.2f}GB)")
        l1 = baseline_throughput.plot(ax=ax[0], y="pravega-pravega-segment-store-0", x="Time", stacked = False, kind="area",color=col1, label=f"Baseline (Total Data Buffered: {throughput_1:.2f}GB)")
    
    baseline_lat.plot(ax=ax[1], y="Cache", x="Time", stacked=False, color = col1, label="Baseline")
    geds_lat.plot(ax=ax[1], y="Cache", x="Time", stacked=False, color = col2, label="GEDS Integrated")

    ax[0].yaxis.set_major_formatter(ticks_x_throughput)
    ax[1].yaxis.set_major_formatter(ticks_x_latency)

    ax[0].set_xlabel("Time Elapsed")
    plt.xlabel(f"Time Elapsed")
    ax[0].grid(visible=True)
    ax[1].grid(visible=True)
    ax[0].set_ylabel("Write Speed")
    ax[1].set_ylabel("Cache Latency") 


    ts_cut = timestamps["timestamp"]["Pause Time"]
    ts_resume = timestamps["timestamp"]["Resume Time"]
    ts_cut_index1 = geds_throughput["Time"][geds_throughput["Time"] == ts_cut].index[0]  
    ts_resume_index1 = geds_throughput["Time"][geds_throughput["Time"] == ts_resume].index[0]  

    cut_x_ps = ts_cut_index1 / geds_throughput["Time"].size
    resume_x_ps= ts_resume_index1 / geds_throughput["Time"].size

    for i in range(2):
        ax[i].annotate("Service Cut", xy=(cut_x_ps,0), xytext=(cut_x_ps, 0.5),textcoords = "axes fraction", xycoords='axes fraction' , arrowprops=dict(arrowstyle="-", facecolor='black'), verticalalignment="top",bbox=dict(boxstyle='square', pad=0, lw=0, fc=(1, 1, 1, 0.7)))
        ax[i].annotate("Service Restored", xy=(resume_x_ps,0), xytext=(resume_x_ps, 0.5),xycoords='axes fraction' , arrowprops=dict(arrowstyle="-", facecolor='black'), verticalalignment="top",bbox=dict(boxstyle='square', pad=0, lw=0, fc=(1, 1, 1, 0.7)))

    geds_buffer_capacity = geds_throughput[(geds_throughput["Time"] >= ts_cut) & (geds_throughput["Time"] <= ts_resume)]["pravega-pravega-segmentstore-0"].sum() / 1e+9
    geds_buffer_time_capacity = (geds_lat["Time"][geds_lat["Cache"].first_valid_index()] - ts_cut).total_seconds()
    baseline_buffer_capacity = baseline_throughput[(baseline_throughput["Time"] >= ts_cut) & (baseline_throughput["Time"] <= ts_resume)]["pravega-pravega-segment-store-0"].sum() / 1e+9
    baseline_buffer_time_capacity = (baseline_lat["Time"][baseline_lat["Cache"].first_valid_index()] - ts_cut).total_seconds()

    with open(outputdir+"\\report.txt", 'w') as file:
        file.write(f"geds_buffer Time: {geds_buffer_time_capacity:.2f} seconds\n")
        file.write(f"geds_buffer Capacity: {geds_buffer_capacity:.2f}Gb\n")
        file.write(f"baseline_buffer Time: {baseline_buffer_time_capacity:.0f} seconds\n")
        file.write(f"baseline_buffer Capacity: {baseline_buffer_capacity:.2f}Gb\n")
        file.write(f"GEDS showed a {geds_buffer_capacity - baseline_buffer_capacity:.2f}Gb improvement in buffer capacity, and a {geds_buffer_time_capacity - baseline_buffer_time_capacity:.0f} second improvement to buffer time.")

    plt.savefig(outputdir + "\\Throughput and Latency Comparative.png",bbox_inches = 'tight') 

def throughput_lat(write_df, latency_df, timestamps, geds=True):
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(18.5,10.5)

    if geds:
        segment_name = "pravega-pravega-segmentstore-0"
    else:
        segment_name = "pravega-pravega-segment-store-0"
    throughput = write_df[segment_name].sum()  / 1e+9
    write_df["Cache"] = latency_df["Cache"]
    write_df.plot(ax = ax, x = "Time", y = segment_name, label=f"Total Data Buffered: {throughput:.2f}GB", kind = "area", stacked = False)
    ax2 = ax.twinx()
    write_df.plot(ax = ax2, x = "Time", y = "Cache", color = col2, kind = "area", stacked = False)
    # latency_df.plot(ax=ax2,y="Cache",x="Time", color=col2, kind = "area",stacked = False)

    ax.yaxis.set_major_formatter(ticks_x_throughput)
    ax2.yaxis.set_major_formatter(ticks_x_latency)
    
    ts_cut = timestamps["timestamp"]["Pause Time"]
    ts_resume = timestamps["timestamp"]["Resume Time"]
    ts_cut_index1 = write_df["Time"][write_df["Time"] == ts_cut].index[0]  

    ts_resume_index1 = write_df["Time"][write_df["Time"] == ts_resume].index[0]  

    cut_x_ps = ts_cut_index1 / write_df["Time"].size
    
    resume_x_ps= ts_resume_index1 / write_df["Time"].size

    ts_cut = timestamps["timestamp"]["Pause Time"]
    ax2.annotate("Long-Term Storage Unavailable", xy=(cut_x_ps,0), xytext=(cut_x_ps, 0.5),textcoords = "axes fraction", xycoords='axes fraction' , arrowprops=dict(arrowstyle="-", facecolor='black'), verticalalignment="top",bbox=dict(boxstyle='square', pad=0, lw=0, fc=(1, 1, 1, 0.7)))
    ax2.annotate("Long-Term Storage Available", xy=(resume_x_ps,0), xytext=(resume_x_ps, 0.5),xycoords='axes fraction' , arrowprops=dict(arrowstyle="-", facecolor='black'), verticalalignment="top",bbox=dict(boxstyle='square', pad=0, lw=0, fc=(1, 1, 1, 0.7)))
    
    handles, labels = ax.get_legend_handles_labels()
    handles1, labels1 = ax2.get_legend_handles_labels()
    fig.legend(handles + handles1, labels + labels1, loc='upper center')
    ax.get_legend().remove()
    ax2.get_legend().remove()
    if geds:
        plt.savefig(outputdir + "\\GEDS throughput and Latency.png",bbox_inches = 'tight') 
    else:
        plt.savefig(outputdir + "\\Baseline throughput and Latency.png",bbox_inches = 'tight') 


def write_latency(df, timestamps, geds=True):
    fig, ax = plt.subplots()
    fig.set_size_inches(18.5,10.5)

    df.plot(ax = ax, x="Time",y=["p0.1","p0.5","p0.9","p0.99","p0.999","p0.9999"])
    ticks_x_latency = ticker.FuncFormatter(lambda x, pos: '{0:g}s'.format(x/1000))
    ax.yaxis.set_major_formatter(ticks_x_latency)

    ts_cut = timestamps["timestamp"]["Pause Time"]
    ts_resume = timestamps["timestamp"]["Resume Time"]
    ts_cut_index1 = df["Time"][df["Time"] == ts_cut].index[0]  
    ts_resume_index1 = df["Time"][df["Time"] == ts_resume].index[0]  

    cut_x_ps = ts_cut_index1 / df["Time"].size
    
    resume_x_ps= ts_resume_index1 / df["Time"].size

    ts_cut = timestamps["timestamp"]["Pause Time"]
    ax.annotate("Service Cut", xy=(cut_x_ps,0), xytext=(cut_x_ps, 0.5),textcoords = "axes fraction", xycoords='axes fraction' , arrowprops=dict(arrowstyle="-", facecolor='black'), verticalalignment="top",bbox=dict(boxstyle='square', pad=0, lw=0, fc=(1, 1, 1, 0.7)))
    ax.annotate("Service Restored", xy=(resume_x_ps,0), xytext=(resume_x_ps, 0.5),xycoords='axes fraction' , arrowprops=dict(arrowstyle="-", facecolor='black'), verticalalignment="top",bbox=dict(boxstyle='square', pad=0, lw=0, fc=(1, 1, 1, 0.7)))
    
    if geds:
        plt.savefig(outputdir + "\\GEDS Write Latency.png", bbox_inches = 'tight') 
    else:
        plt.savefig(outputdir + "\\Baseline Write Latency.png", bbox_inches = 'tight') 
        


def cache_use(df, timestamps, df2 = None, geds=True):

    if geds:
        segment_name = "pravega-pravega-segmentstore-0"
    else:
        segment_name = "pravega-pravega-segment-store-0"

    if df2 == None:
        fig, ax = plt.subplots()
        fig.set_size_inches(18.5,10.5)

        df.plot(ax = ax, x = "Time", y = segment_name, kind = "area", stacked = False)
        ticks_x_throughput = ticker.FuncFormatter(lambda x, pos: '{0:g}Mb'.format(x/1e6))
        ax.yaxis.set_major_formatter(ticks_x_throughput)
    else:
        fig, ax = plt.subplots(2,1)
        fig.set_size_inches(18.5,10.5)

        df.plot(ax=ax[0], x = "Time", y = "pravega-pravega-segmentstore-0", kind = "area", stacked = False)
        ticks_x_throughput = ticker.FuncFormatter(lambda x, pos: '{0:g}Mb'.format(x/1e6))
        ax[0].yaxis.set_major_formatter(ticks_x_throughput)

        df2.plot(ax=ax[1], x = "Time", y = "pravega-pravega-segmentstore-0", kind = "area", stacked = False)
        ticks_x_throughput = ticker.FuncFormatter(lambda x, pos: '{0:g}Mb'.format(x/1e6))
        ax[1].yaxis.set_major_formatter(ticks_x_throughput)

    ts_cut = timestamps["timestamp"]["Pause Time"]
    ts_resume = timestamps["timestamp"]["Resume Time"]
    ts_cut_index1 = df["Time"][df["Time"] == ts_cut].index[0]  
    ts_resume_index1 = df["Time"][df["Time"] == ts_resume].index[0]  

    cut_x_ps = ts_cut_index1 / df["Time"].size
    
    resume_x_ps= ts_resume_index1 / df["Time"].size

    ts_cut = timestamps["timestamp"]["Pause Time"]
    ax.annotate("Service Cut", xy=(cut_x_ps,0), xytext=(cut_x_ps, 0.5),textcoords = "axes fraction", xycoords='axes fraction' , arrowprops=dict(arrowstyle="-", facecolor='black'), verticalalignment="top",bbox=dict(boxstyle='square', pad=0, lw=0, fc=(1, 1, 1, 0.7)))
    ax.annotate("Service Restored", xy=(resume_x_ps,0), xytext=(resume_x_ps, 0.5),xycoords='axes fraction' , arrowprops=dict(arrowstyle="-", facecolor='black'), verticalalignment="top",bbox=dict(boxstyle='square', pad=0, lw=0, fc=(1, 1, 1, 0.7)))
    
    if geds:
        plt.savefig(outputdir + "\\GEDS cache use.png",bbox_inches = 'tight') 
    else:
        plt.savefig(outputdir + "\\Baseline cache use.png",bbox_inches = 'tight') 




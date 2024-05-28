import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
import math

def tick_formatter(x, pos):
    min = math.floor(x / 60 /2) 
    return f"{min}m"



df = pd.read_csv("10-5_h7m50\Segment Store Cache Used Size-data-2024-05-10 07_46_53.csv")
df["pravega-pravega-segment-store-0"].fillna(0,inplace=True)
df["pravega-pravega-segment-store-0"] = df["pravega-pravega-segment-store-0"] / 1000000
fig, ax = plt.subplots(1,1)
fig.set_size_inches(18.5,10.5)
df.plot(ax=ax,use_index=True,y="pravega-pravega-segment-store-0",kind="area", stacked=False)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(tick_formatter))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%dMB'))


plt.show()

# def comparative_graph(write_df1, write_df2, latency_df1, latency_df2):
#     fig, ax = plt.subplots(2,1)
#     fig.set_size_inches(18.5,10.5)
#     col1 = "steelblue"
#     col2 = "orange"
#     throughput_1 = write_df1["pravega-pravega-segment-store-0"].sum()  / 1e+9
#     throughput_2 = write_df2["pravega-pravega-segment-store-0"].sum()  / 1e+9

#     l1 = write_df2.plot(ax=ax[0], use_index=True, y="Throughput", stacked = False, kind="area",color=col2, label=f"Baseline (Throughput: {throughput_2:.2f}GB)")
#     l2 = write_df1.plot(ax=ax[0], use_index=True, y="Throughput", stacked = False, kind="area",color=col1, label=f"GEDS Integrated (Throughput: {throughput_1:.2f}GB)")
    
#     latency_df2.plot(ax=ax[1], y="Cache",use_index=True, stacked=False, color = col2, label="GEDS Integrated")
#     latency_df1.plot(ax=ax[1], y="Cache",use_index=True, stacked=False, color = col1, label="Baseline")

#     ax[0].yaxis.set_major_formatter(ticker.FormatStrFormatter('%dMB/s'))
#     ax[0].xaxis.set_major_formatter(ticker.FuncFormatter(tick_formatter))

#     ax[0].set_xlabel("Time Elapsed (Seconds)")
#     plt.xlabel(f"Time Elapsed (Seconds)")
#     ax[0].grid(visible=True)
#     ax[0].set_ylabel("Write Speed")
#     ax[1].set_ylabel("Cache Latency")
#     ax[1].xaxis.set_major_formatter(ticker.FuncFormatter(tick_formatter))
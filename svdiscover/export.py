import csv

def export_to_csv(out_filepath, record_list, header=None):
    """Simple utility to export SQLite records to a CSV
    
    Arguments:
        out_filepath {str} -- Filepath+name of output file
        record_list {list} -- List of lists containing SQLite database records
    """    
    with open(out_filepath, "w") as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(record_list)

# def plot_anchor_timediff(records, centerpoint, zoom=5):
#     map_obj = folium.Map(
#         location=centerpoint,
#         zoom_start=zoom
#     )

#     for r in records:
#         if r[-1] <= 2:
#             color = 'red'
#         elif r[-1] >= 3 and r[-1] < 6:
#             color = 'orange'
#         else:
#             color = 'green'

#         folium.Marker(
#             location=[r[1], r[0]],
#             #popup=f"{records[r][0][0]}",
#             icon=folium.Icon(color=color)
#         ).add_to(map_obj)
#     return map_obj

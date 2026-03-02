from pystac_client import Client
import planetary_computer
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, mapping
import rioxarray


# Polygon Coordinates

#  insert your coordinates of the polygon 
coords = [
   
]

polygon = Polygon(coords)
bbox = polygon.bounds

# Connect to STAC API

catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

# search the sentinel satellite with the date time and the band distance 
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=bbox,
    datetime="2026-02-01/2026-02-28",
    query={"eo:cloud_cover": {"lt": 20}}
)

# get the items form the search 
items = list(search.items())
# 
item = planetary_computer.sign(items[0])

# Load Bands

red = rioxarray.open_rasterio(item.assets["B04"].href).squeeze()
nir = rioxarray.open_rasterio(item.assets["B08"].href).squeeze()
green = rioxarray.open_rasterio(item.assets["B03"].href).squeeze()
blue = rioxarray.open_rasterio(item.assets["B02"].href).squeeze()

# Clip to Polygon
red = red.rio.clip([mapping(polygon)], crs="EPSG:4326")
nir = nir.rio.clip([mapping(polygon)], crs="EPSG:4326")
green = green.rio.clip([mapping(polygon)], crs="EPSG:4326")
blue = blue.rio.clip([mapping(polygon)], crs="EPSG:4326")

red = red.astype(float)
nir = nir.astype(float)
green = green.astype(float)
blue = blue.astype(float)

# Calculate Indices
ndvi = (nir - red) / (nir + red)
ndwi = (green - nir) / (green + nir)
evi = 2.5 * ((nir - red) / (nir + 6*red - 7.5*blue + 1))

# Convert to numpy
ndvi_np = ndvi.values
ndwi_np = ndwi.values
evi_np = evi.values

# Plot and Save Function
def plot_and_save(data, title, cmap, filename):
    plt.figure(figsize=(6,6))
    plt.imshow(data, cmap=cmap)
    plt.colorbar()
    plt.title(title)
    plt.axis('off')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

# Generate Images

plot_and_save(ndvi_np, "NDVI", "RdYlGn", "ndvi.png")
plot_and_save(ndwi_np, "NDWI", "Blues", "ndwi.png")
plot_and_save(evi_np, "EVI", "viridis", "evi.png")


# Save GeoTIFF also

ndvi.rio.to_raster("ndvi.tif")
ndwi.rio.to_raster("ndwi.tif")
evi.rio.to_raster("evi.tif")

print("NDVI Mean:", float(np.nanmean(ndvi_np)))
print("NDWI Mean:", float(np.nanmean(ndwi_np)))
print("EVI Mean:", float(np.nanmean(evi_np)))

print("Images saved:")
print("ndvi.png, ndwi.png, evi.png")
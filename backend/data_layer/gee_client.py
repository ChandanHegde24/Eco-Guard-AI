import ee

# Ensure Earth Engine is initialized when this module is imported
try:
    ee.Initialize()
except Exception as e:
    print(f"Error initializing Earth Engine: {e}. Please run ee.Authenticate() first.")

def mask_s2_clouds(image):
    """
    Applies cloud masking to Sentinel-2 imagery using the QA60 band[cite: 20, 23].
    """
    qa = image.select('QA60')

    # Bits 10 and 11 are clouds and cirrus, respectively.
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    # Both flags should be set to zero, indicating clear conditions.
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0) \
        .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))

    return image.updateMask(mask).divide(10000)


def fetch_satellite_images(latitude: float, longitude: float, time_t1: str, time_t2: str, buffer_meters: int = 5000):
    """
    Fetches cloud-masked Sentinel-2 imagery for two distinct time periods around a specific coordinate.
    
    Args:
        latitude: Center point latitude.
        longitude: Center point longitude.
        time_t1: Start date string (e.g., '2025-01-01').
        time_t2: End date string (e.g., '2026-01-01').
        buffer_meters: The radius around the point to define the Region of Interest (ROI).
        
    Returns:
        A dictionary containing the median mosaic images for T1 and T2.
    """
    # Define the Region of Interest (ROI)
    point = ee.Geometry.Point([longitude, latitude])
    roi = point.buffer(buffer_meters)

    # Load the Sentinel-2 Surface Reflectance collection [cite: 20]
    dataset = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterBounds(roi) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                .map(mask_s2_clouds)

    # We typically need a date range for each "time" to get a clean cloud-free mosaic.
    # For simplicity, we'll look at a 30-day window around the target dates.
    t1_start = ee.Date(time_t1)
    t1_end = t1_start.advance(30, 'day')
    
    t2_start = ee.Date(time_t2)
    t2_end = t2_start.advance(30, 'day')

    # Create median composites for the T1 and T2 windows
    image_t1 = dataset.filterDate(t1_start, t1_end).median().clip(roi)
    image_t2 = dataset.filterDate(t2_start, t2_end).median().clip(roi)

    # In a full deployment, you would likely export these images to Google Cloud Storage 
    # or process them directly as NumPy arrays using libraries like geemap or rasterio.
    return {
        "t1": image_t1,
        "t2": image_t2,
        "roi": roi
    }
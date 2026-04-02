import ee
from core.config import settings


class EarthEngineUnavailableError(RuntimeError):
    """Raised when Earth Engine is not ready to serve satellite requests."""

# Track whether Earth Engine was initialized successfully
ee_initialized = False

try:
    ee.Initialize(project=settings.EE_PROJECT_ID)
    ee_initialized = True
    print("Earth Engine initialized successfully.")
except Exception as e:
    print(f"Warning: Earth Engine not initialized: {e}")
    print("The server will start, but satellite data endpoints require authentication.")
    print("Run 'earthengine authenticate' in your terminal to enable full functionality.")

def mask_s2_clouds(image):
    """
    Applies cloud masking to Sentinel-2 imagery using the QA60 band.
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
    """
    if not ee_initialized:
        raise EarthEngineUnavailableError(
            "Google Earth Engine is not authenticated. "
            "Please run 'earthengine authenticate' in your terminal first."
        )

    # Define the Region of Interest (ROI)
    point = ee.Geometry.Point([longitude, latitude])
    roi = point.buffer(buffer_meters)

    # Load the Sentinel-2 Surface Reflectance collection
    dataset = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterBounds(roi) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                .map(mask_s2_clouds)

    # We typically need a date range for each "time" to get a clean cloud-free mosaic.
    t1_start = ee.Date(time_t1)
    t1_end = t1_start.advance(30, 'day')

    t2_start = ee.Date(time_t2)
    t2_end = t2_start.advance(30, 'day')

    # Create median composites for the T1 and T2 windows
    image_t1 = dataset.filterDate(t1_start, t1_end).median().clip(roi)
    image_t2 = dataset.filterDate(t2_start, t2_end).median().clip(roi)

    return {
        "t1": image_t1,
        "t2": image_t2,
        "roi": roi
    }

def get_image_thumbnail(image, roi):
    """Generates a visual RGB thumbnail URL for the frontend rendering."""
    if not ee_initialized:
        return None
    try:
        # Visualize True Color surface reflectance (B4=Red, B3=Green, B2=Blue)
        vis_params = {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0,
            'max': 0.3,
            'region': roi,
            'dimensions': 600,
            'format': 'jpg'
        }
        return image.getThumbURL(vis_params)
    except Exception as e:
        print(f"Failed to generate thumbnail: {e}")
        return None

import ee

def calculate_ndvi(image):
    """
    Calculates the Normalized Difference Vegetation Index (NDVI) to measure forest health.
    Formula: (NIR - Red) / (NIR + Red)
    Sentinel-2 Bands: B8 (NIR) and B4 (Red)
    """
    # Computes the standard NDVI formula and adds it as a new band to the image
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)


def calculate_ndwi(image):
    """
    Calculates the Normalized Difference Water Index (NDWI) to detect water bodies.
    Formula: (Green - NIR) / (Green + NIR)
    Sentinel-2 Bands: B3 (Green) and B8 (NIR)
    """
    # Computes the standard NDWI formula and adds it as a new band to the image
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
    return image.addBands(ndwi)


def analyze_environmental_change(image_t1, image_t2, index_type="NDVI"):
    """
    Compares the index between Time T1 and Time T2 to calculate pixel-level differences.
    """
    # First, calculate the requested index for both time periods
    if index_type == "NDVI":
        t1_processed = calculate_ndvi(image_t1).select('NDVI')
        t2_processed = calculate_ndvi(image_t2).select('NDVI')
    elif index_type == "NDWI":
        t1_processed = calculate_ndwi(image_t1).select('NDWI')
        t2_processed = calculate_ndwi(image_t2).select('NDWI')
    else:
        raise ValueError("Invalid index_type. Choose 'NDVI' or 'NDWI'.")

    # Perform pixel-level difference analysis (T2 - T1)
    change_image = t2_processed.subtract(t1_processed).rename(f'{index_type}_Change')
    
    # Calculate the percentage of change across the Region of Interest (ROI)
    # Note: In a full PyTorch setup, this change_image would be fed into your Siamese CNN.
    # For a deterministic baseline, we can calculate the mean change over the area.
    
    mean_change = change_image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=image_t1.geometry(),
        scale=10, # Sentinel-2 resolution is 10 meters
        maxPixels=1e9
    )
    
    # Convert the raw index change to a rough percentage for risk scoring
    # (This is a simplified abstraction of what your AI classification would output)
    change_value = mean_change.get(f'{index_type}_Change').getInfo()
    percentage_change = abs(change_value * 100) if change_value else 0.0
    
    return percentage_change
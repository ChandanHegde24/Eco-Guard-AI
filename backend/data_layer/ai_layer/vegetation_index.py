import ee

def calculate_ndvi(image):
    """
    Calculates the Normalized Difference Vegetation Index (NDVI) to measure forest health.
    """
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)

def calculate_ndwi(image):
    """
    Calculates the Normalized Difference Water Index (NDWI) to detect water bodies.
    """
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
    return image.addBands(ndwi)

def analyze_environmental_change(image_t1, image_t2, index_type="NDVI"):
    """
    Compares the index between Time T1 and Time T2 to calculate pixel-level differences.
    """
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
    mean_change = change_image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=image_t1.geometry(),
        scale=10, 
        maxPixels=1e9
    )
    
    change_value = mean_change.get(f'{index_type}_Change').getInfo()
    percentage_change = abs(change_value * 100) if change_value else 0.0
    
    return percentage_change
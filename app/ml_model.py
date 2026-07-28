def predict_crop(temp, rain, humidity):
    """
    Enhanced rule-based crop predictor.
    
    This simulates an ML model by considering interactions between 
    temperature, rainfall, and humidity.
    """
    
    # 1. High Rainfall Logic
    if rain > 200:
        if temp < 20:
            return "Wheat" 
        return "Rice"
    
    # 2. High Temperature & Arid Logic
    if temp > 32:
        if humidity < 40:
            return "Sugarcane" 
        return "Maize" 
    
    # 3. Moderate Conditions
    if 20 <= temp <= 30:
        if humidity > 75:
            return "Rice" 
        if rain > 100:
            return "Maize"
        return "Wheat"
    
    # 4. Cooler/Drier Conditions
    if temp < 20:
        return "Wheat"
        
    return "Maize" 
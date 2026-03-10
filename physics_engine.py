import math
# South African TRH17/ SANRAL Geometric Design Physics Engine

# =======================================
# STEP 1: SOUTH AFRICAN STANDARDS LIBRARY
# =======================================

# TRH17 FRICTION FACTORS (f_l) - Used for SSD
friction_longitudinal = {
    120: 0.28,
    100: 0.29,
    80: 0.31,
    60: 0.33,
    40: 0.38
}

# TRH17 Lateral Friction Factors (f_s) - Used for horizontal curve design
friction_lateral = {
    120: 0.11,
    100: 0.14,
    80: 0.15,
    60: 0.17,
    40: 0.17
}

# STANDARD DRIVER REACTION TIME (t) in seconds
Reaction_Time_Rural = 2.5
Reaction_Time_Urban = 2.0

# MAX SUPERELEVATION LIMITS (e_max)
E_MAX_RURAL = 0.06    #6% crossfall
E_MAX_MOUNTAINOUS = 0.10  #10% crossfall

# =======================================
# STEP 2: SIGHT DISTANCE CALCULATIONS
# =======================================

def calculate_ssd(speed, gradient_percentage, environment="Rural"):
    """
    Calculates SSD per SANRAL/TRH17.
    gradient percentage: positive for uphill (+4), negative for downhill (-4).
    """
    if speed not in friction_longitudinal:
        return "ERROR: Speed must be per TRH17 table (120, 100, 80, 60, 40 km/h)."
    
    f_l = friction_longitudinal[speed]
    t = Reaction_Time_Rural if environment == "Rural" else Reaction_Time_Urban

    #1. Calculate Braking Distance (d1)
    # The distance traveled before the driver hits the breaks
    d1 = 0.278 * speed * t

    #2. Calculate Braking Distance (d2)
    # Convert gradient percentage to a decimal for the formula
    G = gradient_percentage / 100

    # Calculate the effective Friction
    # If going downhill on ice, theoretically could have negative friction, but we'll cap it at zero for safety
    effective_friction = f_l + G
    if effective_friction <= 0.01:
        return "CRITICAL ERROR: Gradient too steep for safe stopping"

    d2 = (speed**2)/ (254*effective_friction)
    # Total SSD
    total_ssd = d1 + d2
    return round(total_ssd, 2)

def get_min_psd(speed):
    """
    Returns the minimum PSD for a given design speed per TRH17.
    """
    psd_table = {
        120: 770,
        100: 600,
        80: 440,
        60: 280,
        40: 160
    }
    return psd_table.get(speed, " NO PSD data for this speed")

# =============================================
# STEP 3: HORIZONTAL ALIGNMENT & SUPERELEVATION
# =============================================
def calculate_horizontal_parameters(speed, radius, e_max=E_MAX_RURAL):
    """
    Calculates the required superelevation and checks against TRH17 minimum radius.
    Returns a dictionary of the exact physics.
    """
    if speed not in friction_lateral:
        return {"status": "ERROR", "message": "Speed not in TRH17 table"}
    f_s = friction_lateral[speed]
    # 1. Calculate min radius (R_min)
    r_min = (speed ** 2) / (127 * (e_max + f_s))

    # 2. Calculate Required Superelevation (e_req) for the actual radius
    e_req = ((speed ** 2) / (127 * radius)) - f_s

    # Cap the req e to the max permitted, or 0 if it's a very flat/large curve
    e_req = max(0.0, min(e_req, e_max))

    status = "PASS" if radius >= r_min else "CRITICAL"

    return {
        "status": status,
        "R_min_required": round(r_min, 2),
        "actual_radius": round(radius, 2),
        "e_required_percent": round(e_req * 100, 2)
    }

def calculate_setting_out_chords(radius, curve_length, interval=20.0):
    """
    Calculates the straight-line chord distances for surveyors to peg the arc on site.
    Defaults to 20m standard intervals.
    """
    chords = []

    # Calculate how many full 20m intervals fit into the curve
    num_full_intervals = int(curve_length // interval)
    remainder = curve_length % interval

    # Calculate the deflection angle (Delta) for the standard interval in radians
    # Arc Length L = R * Delta => Delta = L/R
    delta_interval = interval / radius

    # The setting‑out chord
    standard_chord = 2 * radius * math.sin(delta_interval / 2)

    for _ in range(num_full_intervals):
        chords.append(round(standard_chord, 3))

    # Handle the remaining distance to the End of Curve (EOC) peg
    if remainder > 0:
        delta_remainder = remainder / radius
        remainder_chord = 2 * radius * math.sin(delta_remainder / 2)
        chords.append(round(remainder_chord, 3))

    return chords
# ==========================================
# STEP 4: VERTICAL ALIGNMENT & CRITICAL POINTS
# ==========================================

def calculate_vertical_geometry(pvi_chainage, pvi_elev, g1, g2, length):
    """
    Calculates all critical points (BVC, EVC, High/Low points) for a vertical curve.
    Gradients (g1, g2) must be in percentages (e.g., 4.5 for 4.5%).
    """
    # 1. K-Value and Curve Type
    A = abs(g2 - g1)
    k_val = length / A if A != 0 else 0
    curve_type = "Crest" if g1 > g2 else "Sag"
    
    # 2. BVC and EVC Chainages (Beginning and End of Vertical Curve)
    bvc_chainage = pvi_chainage - (length / 2.0)
    evc_chainage = pvi_chainage + (length / 2.0)
    
    # 3. BVC and EVC Elevations
    # Gradient is divided by 100 to convert percentage to a decimal slope
    bvc_elev = pvi_elev - ((g1 / 100.0) * (length / 2.0))
    evc_elev = pvi_elev + ((g2 / 100.0) * (length / 2.0))
    
    # 4. Turning Point (High / Low Point) for Drainage
    # A true turning point only exists if the gradients cross 0% (e.g., uphill to downhill)
    turn_chainage = None
    turn_elev = None
    
    if (g1 > 0 and g2 < 0) or (g1 < 0 and g2 > 0):
        # Distance X from BVC to the turning point
        x_turn = (g1 * length) / (g1 - g2)
        turn_chainage = bvc_chainage + x_turn
        
        # Parabolic elevation formula at distance X
        turn_elev = bvc_elev + ((g1 / 100.0) * x_turn) + (((g2 - g1) / (200.0 * length)) * (x_turn ** 2))
        
    return {
        "Curve_Type": curve_type,
        "K_Value": round(k_val, 2),
        "A_Value": round(A, 2),
        "BVC_CH": round(bvc_chainage, 3),
        "BVC_Elev": round(bvc_elev, 3),
        "EVC_CH": round(evc_chainage, 3),
        "EVC_Elev": round(evc_elev, 3),
        "Turn_CH": round(turn_chainage, 3) if turn_chainage else "N/A",
        "Turn_Elev": round(turn_elev, 3) if turn_elev else "N/A"
    }
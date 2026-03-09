print("--- Road Design Gradient Check ---")
gradients = [2.5, 4.0, 8.5, -3.0, 11.2]
for g in gradients:
    if abs(g) > 10.0:
        status = "CRITICAL: Exceeds standard"
    else:
        status = "PASS"
    print(f"Gradient:{g}%| Status: {status}")
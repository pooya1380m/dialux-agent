# DIALux evo basics

DIALux evo is free lighting design software from DIAL GmbH for interior and exterior lighting calculations.
It has no public REST or scripting API. Integration is via file exchange: luminaire data in LDT (Eulumdat), IES and ULD formats, CAD/BIM exchange via DWG, DXF and IFC, and reports exported as PDF.
Manufacturers provide catalogs through a plugin interface. UI automation on Windows (pywinauto) is a last resort.

# Standards

EN 12464-1 defines maintained illuminance, uniformity (U0), glare (UGR) and colour rendering (Ra) for indoor workplaces. Offices typically need 500 lux, U0 0.6, UGR 19, Ra 80.
EN 1838 covers emergency lighting: escape route illuminance at least 1 lux on the centre line, and open-area anti-panic lighting at least 0.5 lux.

# Lumen method

Number of luminaires = target lux x area / (flux x utilance x maintenance factor). Room index k = L x W / (h x (L + W)) where h is height above the workplane.

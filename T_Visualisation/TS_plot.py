from visualisation_func import TS_Plot, ICCG_Comp_Plot, AMP_Plot

# Plotting Example (IC, CG, Total, IC vs. CG)
TS_Plot(0, 600, "IC", "20141127", "Brisbane", 6)
TS_Plot(0, 720, "CG", "20141127", "Brisbane", 6)
TS_Plot(200, 520, "Total", "20141127", "Brisbane", 6)
ICCG_Comp_Plot(0, 720, "20141127", "Brisbane", 6)
AMP_Plot(0, 720, "20141127", "Brisbane", 8, "IC_abs_amp")
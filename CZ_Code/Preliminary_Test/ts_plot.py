from LJ_FUNCTION import TS_Plot, ICCG_Comp_Plot, AMP_Plot, file_count, ClusterTS_Plot
# Plotting Example (IC, CG, Total, IC vs. CG)
# Feel free to change the first three variables in the following command to obtain a different plot
# TS_Plot(0, 720, "IC", "20141127", "Brisbane", 8)
# TS_Plot(0, 720, "CG", "20141127", "Brisbane", 8)
# TS_Plot(200, 520, "Total", "20141127", "Brisbane", 8)
# ICCG_Comp_Plot(0, 720, "20141127", "Brisbane", 8)
# AMP_Plot(0, 720, "20141127", "Brisbane", 8, "IC_abs_amp")
# AMP_Plot(0, 720, "20141127", "Brisbane", 8, "CG_abs_amp")
# AMP_Plot(0, 720, "20141127", "Brisbane", 8, "Total_abs_amp")
ClusterTS_Plot("Cluster_InfoCSV/", "Mitcham_2022-09-18", 2)
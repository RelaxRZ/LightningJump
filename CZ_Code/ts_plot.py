from LJ_FUNCTION import TS_Plot, ICCG_Comp_Plot, AMP_Plot, file_count, ClusterTS_Plot, ClusterTS_Plot_NoRadar, ClusterTS_Plot_NoSHI, ClusterTS_Plot_SHI
# Plotting Example (IC, CG, Total, IC vs. CG)
# Feel free to change the first three variables in the following command to obtain a different plot
# TS_Plot(0, 720, "IC", "20141127", "Brisbane", 8)
# TS_Plot(0, 720, "CG", "20141127", "Brisbane", 8)
# TS_Plot(200, 520, "Total", "20141127", "Brisbane", 8)
# ICCG_Comp_Plot(0, 720, "20141127", "Brisbane", 8)
# AMP_Plot(0, 720, "20141127", "Brisbane", 8, "IC_abs_amp")
# AMP_Plot(0, 720, "20141127", "Brisbane", 8, "CG_abs_amp")
# AMP_Plot(0, 720, "20141127", "Brisbane", 8, "Total_abs_amp")
ClusterTS_Plot("Cluster_InfoCSV/Variable_Case_1/", "Brisbane_2021-10-30", 2, "Variable_Case_1/")
ClusterTS_Plot_NoRadar("Cluster_InfoCSV/Variable_Case_1/", "Brisbane_2021-10-30", 2, "Variable_Case_1/")
ClusterTS_Plot_NoSHI("Cluster_InfoCSV/Variable_Case_1/", "Brisbane_2021-10-30", 2, "Variable_Case_1/")
ClusterTS_Plot_SHI("Cluster_InfoCSV/Variable_Case_1/", "Brisbane_2021-10-30", 2, "Variable_Case_1/")
(defun c:AutoDTM ( / csv_file)
  (vl-load-com)
  
  ;; 1. Prompt the engineer to select the cleaned CSV
  (setq csv_file (getfiled "Select the CLEAN_PNEZD CSV File" "" "csv" 0))

  (if csv_file
    (progn
      (princ "\n>> Importing 24,000 Points... Please wait...")
      
      ;; 2. Import Points (PENZD format, Add to Group "DTM_POINTS", No elevation/coord adjustments)
      (command "-ImportPoints" "PENZD (comma delimited)" csv_file "Y" "DTM_POINTS" "N" "N")

      (princ "\n>> Building TIN Surface...")
      
      ;; 3. Create a blank TIN Surface named "Existing_Ground"
      (command "-CreateSurface" "TIN" "Existing_Ground" "" "")

      ;; 4. Feed the points into the surface
      (command "-AddPtGroupToSurface" "Existing_Ground" "DTM_POINTS")

      (princ "\n[SUCCESS] Surface Generated! Zooming to extents...")
      (command "ZOOM" "E")
    )
    (princ "\n[ERROR] No file selected.")
  )
  (princ)
)
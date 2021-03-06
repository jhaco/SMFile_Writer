## SMFile_Writer
###### Stepmania File Writer for the [Stepmania Note Generator](https://github.com/cpuguy96/stepmania-note-generator) by cpuguy96 for [Stepmania](https://github.com/stepmania/stepmania/wiki/sm) by VR0. Used in conjunction with the [Stepmania File Parser](https://github.com/jhaco/SMFile_Parser). Converts all .txt file generated by either [Stepmania File Parser](https://github.com/jhaco/SMFile_Parser) or [Stepmania Note Generator](https://github.com/cpuguy96/stepmania-note-generator) to .sm files playable by Stepmania.

# NOTICE: Project moved to [Stepmania Data Tools](https://github.com/jhaco/SMDataTools)

#### Usage:

- Place the output files into the input folder and run the script. The default input folder is `writeIn`.
- Successfully converted files will be generated in the output folder. The default output folder is `writeOut`.
- If different folders are used, specify them by appending `--input inputfolder` and/or `--output outputfolder`.
        Example: `python smfile_writer.py --input inputfolder --output outputfolder`

###### If either arguments are not specified, the scripts uses the default folder where none is specified.
###### If the specified input folder is not found, the script will print an error and terminate.
###### If the specified output folder is not found, the script will automatically generate the missing folder.

---

<details close>
  <summary>Changelog</summary>
        
  Sorted by most recent:
  
  - rewrote the output function to use write to file only once, reducing avg. runtime by 50% (200 sets: 30s to 17s)
  - refactored code
  - rewrote algorithms, reducing average runtime by 25% (on a data set of 200 pairs of txt/ogg files: 40s to 30s)
  - added auto-create folder for each successfully parsed file; allows easier drag/drop to Stepmania's songs 
  - updated to match smfile_parser's multiple difficulty support
  - implemented code changes from smfile_parser
  - reorganized code for readability and added folders
  - removed some redundant code
  - successfully compressed 1/256th measures to as low as 1/4th
  - corrected 1/192th note timings to 1/256th
  - fixed a bug where notes that intersect multiple measures appeared in both measures, resulting in extra notes
  
</details>

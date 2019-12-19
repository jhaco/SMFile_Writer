## SMFile_Writer
#### Stepmania File Writer for the [Stepmania Note Generator](https://github.com/cpuguy96/stepmania-note-generator) by cpuguy96 for [Stepmania](https://github.com/stepmania/stepmania/wiki/sm) by VR0. Used in conjunction with the [Stepmania File Parser](https://github.com/jhaco/SMFile_Parser) by me

Converts all .txt file generated by either [Stepmania File Parser](https://github.com/jhaco/SMFile_Parser) or [Stepmania Note Generator](https://github.com/cpuguy96/stepmania-note-generator) in the writeIn folder generated by smfile_writer.py into .sm files usable by Stepmania

---

#### changelog (top-new):
- reorganized code for readability and added folders
- removed some redundant code
- successfully compressed 1/256th measures to as low as 1/4th
- corrected 1/192th note timings to 1/256th
- fixed a bug where notes that intersect multiple measures appeared in both measures, resulting in extra notes

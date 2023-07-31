# BDR-gpx

## Some scripts to cleanup the BDR gpx files
- Consistent file naming with date
- Consistent track colors (+ import support for Gaia)
  - Alternating Blue/DarkBlue for the main route
  - Red for expert/hard
  - Green for easy/bypass
  - Magenta for connectors / alternates
- Add missing elevation data using Google Maps Elevation API
- Remove time elements from trkpt
  - This data is not consistently there, messes up time display in Gaia
- Text description/comment cleanup - thousands of newlines in some files
- Remove duplicate points that are adjacent to within ~1.1m resolution
- Others?
  - Perhaps remove connectors from actual route files?

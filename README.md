# BDR-gpx

## Some scripts to cleanup the BDR gpx files
- Consistent file naming with date
- Consistent track colors (+ import support for Gaia)
  - Alternating Blue/DarkBlue for the main route
  - Red for expert/hard
  - Green for easy/bypass
  - Magenta for connectors / alternates
- Add missing elevation data using Google Maps Elevation API
- Remove duplicate points that are adjacent to within ~1.1m resolution
  - Reduces file sizes CABDR-N 7.8M -> 4.7M
- Remove time elements from trkpt
  - This data is not consistently there, messes up time display in Gaia
  - Perhaps we can infer from garmin device sample rate the actual travel time?
- Text description/comment cleanup - thousands of newlines in some files
- Others?
  - Perhaps remove connectors from actual route files?
  - Consistent track naming?

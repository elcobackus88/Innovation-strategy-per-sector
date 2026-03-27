# Innovation-strategy-per-sector
The questions I wanted to answer was how innovation in the Netherlands compares per sector, and which patent strategy is favored per sector. 

Patent Strategy by Technology Area (EPO vs OCNL)

This project analyzes how patenting strategies differ across technology areas in the Netherlands by comparing patent applications filed via the European Patent Office (EPO) and Octrooicentrum Nederland (OCNL). Using CBS patent statistics by CPC technology area, the analysis visualizes (1) the EPO share (%) of patent applications to indicate international versus domestic orientation, and (2) the absolute number of patent applications filed via EPO and OCNL. The results show that some technology areas (e.g. medical and measurement technologies) are strongly internationally oriented, while others rely more on national patenting, and that international orientation does not necessarily coincide with high patent volume.

How to run the code:
The analysis uses a single entry point: main.py. Run the script with Python 3.9 or higher. It is recommended to use a virtual environment. Install dependencies with:
pip install pandas matplotlib numpy cbsodata
Then execute:
python main.py
Running the script downloads the data, processes the latest available year, and generates two figures: a horizontal bar chart of EPO share (%) by technology area and a grouped horizontal bar chart of absolute EPO vs OCNL patent applications (ranked by total volume). The figures are saved as PNG files and shown on screen.

Data source:
Data comes from Statistics Netherlands (CBS), dataset “Patentaanvragers en patentaanvragen; technologiegebied (CPC)”, table ID 86217NED.
Link: https://www.cbs.nl/nl-nl/cijfers/detail/86217NED
The data is accessed programmatically via the CBS Open Data (OData) API using the Python package cbsodata; no manual downloads are required.

Notes on interpretation:
Technology areas follow the CPC classification used by CBS. If a patent application relates to multiple technology areas, it is fully counted in each area, meaning totals across areas may exceed overall totals. All data retrieval, processing, and visualization steps are contained in main.py, making the analysis fully reproducible.

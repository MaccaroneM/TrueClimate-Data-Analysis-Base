#DATAMANAGER

import pandas as pd
from pathlib import Path
from datetime import datetime
from generalfunctions import check_float

class DataManager:
    def __init__(self):
        self.api_pull = None
        self.sheets = []
        self.unit_conversions = {
            "kg/hr": ("direct_annual", lambda v: v * 24 * 365 / 1e9 * 29.8),
            "tonnes co2/year": ("direct_annual", lambda v: v / 1e6),
            "ttpa": ("direct_annual", lambda v: v * 1000 / 1e6),

            "mtco2": ("direct_total", lambda v: v),
            "co2e": ("direct_total", lambda v: v),

            "bbl": ("potential_total", lambda v: v * 0.43),
            "boe": ("potential_total", lambda v: v * 0.43),

            "m3": ("potential_total", lambda v: v * 0.0019),
            "m³": ("potential_total", lambda v: v * 0.0019),

            "kg/hr_ch4": ("methane_annual", lambda v: v * 24 * 365 / 1e9),
        }
    def fetch_api_data(self):
        #IN THE FUTURE WILL CALL API OF CHOICE
        pass #here so that I can leave this function as a placeholder
    def infer_sector(self, file_name, sheet_name):
        """Renames sectors, so that they are easily accessible for me to code with"""
        file_lower = file_name.lower()
        sheet_lower = sheet_name.lower()
        if ("plant" in file_lower or "plant" in sheet_lower) and "coal" in file_lower:
            return "coal plants"
        if ("mine" in file_lower or "mine" in sheet_lower) and "coal" in (file_lower + sheet_lower):
            return "coal mines"
        if "extraction" in file_lower or "extraction" in sheet_lower:
            return "oil and gas extraction"
        if "reserves" in sheet_lower and "oil" in file_lower:
            return "oil and gas extraction"
        if "plume" in sheet_lower:
            return "methane plumes"
        if "pipeline" in sheet_lower:
            return "pipelines"
        if "lng" in sheet_lower:
            return "lng terminals"
        if "steel" in file_lower and "iron" not in file_lower:
            return "steel"
        if "iron" in file_lower or "furnace" in sheet_lower:
            return "iron"
        return "unknown"
    def normalize_value(self, value, unit):
        if not check_float(value):
            return None, None
        value = float(value)
        unit = str(unit).lower() if unit else ""
        for key, (dtype, func) in self.unit_conversions.items():
            if key in unit:
                return func(value), dtype
        return None, None
    def estimate_years_active(self, year):
        if not check_float(year):
            return None
        year = float(year)
        if pd.isna(year):
            return None
        current = datetime.now().year
        years = current - year
        if years <= 0:
            return None
        return years

    def load_energy_monitor_data(self):
        """Loads spreadsheets from folder and places them into sheets variable for later cleaning"""
        folder = Path("dataspreadsheets/global_energy_monitor")         #Creates a path to go to datafiles

        for data_file in folder.rglob("*.xlsx"):                        #Loops through datafiles and reads spreadsheets
            print(f"READING: {data_file.name}")                         #Console update

            sheets = pd.read_excel(data_file, sheet_name=None)          #Appending sheets to sheet list

            for sheet_name, df in sheets.items():                       #Looping through sheet
                if ("about" not in sheet_name.lower()
                        and "change" not in sheet_name.lower()
                        and "relining" not in sheet_name.lower()):      #Checking whether the sheet subsections are usable (FILTERING)
                    key = f"{data_file.stem}_{sheet_name}"              #used later in console message
                    sector = self.infer_sector(data_file.name, sheet_name)
                    self.sheets.append({                                #developing data frame
                        "file": data_file.name,
                        "sheet": sheet_name,
                        "sector": sector,
                        "data": df
                    })
                    print(f"\tStored: {key}, Rows: {len(df)}")          #console success message, iterates through number of rows with df (pandas thing)
                else:
                    print(f"\tSkipped: {sheet_name}")

    def find_column(self, df, keyword_weights):
        """Function to find columns within fed spreadsheets based on a given score system"""
        best_col = None
        best_score = 0
        for col in df.columns:
            col_str = str(col)
            col_lower = col.lower()
            score = 0
            for keyword, weight in keyword_weights.items(): #looping through fed grading system
                if keyword in col_lower:
                    score += weight                         #Grading
            if score > best_score:                          #Evaluating all grades
                best_score = score
                best_col = col_str
        if best_score <= 0:                                 #Testing if nothing was detected
            return None                                     #Returns an empty column name to show in terminal, for problemsolving
        return best_col                                     #Spits out highest graded result

    def infer_unit_from_column(self, col_name, raw_ch4=False):
        if not col_name:
            return None
        col = col_name.lower()
        if "cmm_emissions" in col or "co2e_20" in col:
            return "co2e"
        if "co2e" in col:
            return "co2e"
        if "kg/hr" in col or "kg_per_hr" in col:
            return "kg/hr_ch4" if raw_ch4 else "kg/hr"
        if "mtco2" in col or "million_tonnes" in col or "mt_co2" in col:
            return "mtco2"
        if "mtpa" in col:  # ADD
            return "mtco2"
        if "ttpa" in col:  # ADD
            return "ttpa"
        if "tonnes" in col or "tonnes_co2" in col:
            return "tonnes co2/year"
        if "bbl" in col or "boe" in col:
            return "bbl"
        if "m3" in col or "m³" in col:
            return "m3"
        return None

    def infer_emissions_type(self, col_name):
        """takes co2 column name and infers the emission type"""
        if not col_name:
            return "unknown"
        col = col_name.lower()
        if "lifetime" in col:
            return "lifetime"
        elif "cmm" in col or "methane" in col: #!!!!!!!
            return "cmm_20yr"
        else:
            return "unknown"

    def clean_data(self):
        """Cleans loaded spreadsheets and organizes them for viz and analysis"""
        for entry in self.sheets:                           #looping through individual sheets
            cleaned_records = []
            sector = entry["sector"]
            df = entry["data"]                              #creating pandas usable object
            df.columns = (                                  #cleans column names
                df.columns
                .map(str)
                .str.strip()                                #no end whitespace
                .str.lower()                                #lowercase
                .str.replace(r"\s+", "_", regex=True)       #replacing spaces with underscores, and handles weird formatting in excel
            )
            """Calling find_column to potentially find columns of best fit, manually assigned grading system"""
            name_col = self.find_column(df, {
                "name": 3,
                "plant": 4,
                "mine_name": 10,
                "project": 2,
                "pipline_name": 5,
                "unit_name": 4,
            })
            country_col = self.find_column(df, {
                "country": 4,
                "nation": 3,
                "country/area": 2,
                "country/areas": 2,
                "area": 1
            })
            year_col = self.find_column(df, {
                "opening": 4,
                "open": 4,
                "year": 1,
                "start_year": 5,
                "start": 2,
            })
            owner_col = self.find_column(df, {
                "owners": 10,
                "owner": 5,
                "operator": 4,
                "parent": 3,
                "company": 6
            })
            unit_col = self.find_column(df, {
                "unit": 5,
                "units": 10,
                "units_(converted)": 50
            })

            co2_col = None
            reserve_col = None
            reserve_unit_col = self.find_column(df, {
                "units": 5,
                "units_(converted)": 50
            })

            if sector in ["coal plants", "coal mines"]:
                co2_col = self.find_column(df, {
                    "cmm_emissions": 20,
                    "lifetime_co2": 10,
                    "co2e": 6,
                    "co2": 4,
                    "cmm": 5,
                    "20": 5,
                    "emission_factor": -10,
                    "mitigation": -20,
                    "associated": -20,
                })
            elif sector == "oil and gas extraction":
                reserve_col = self.find_column(df, {
                    "quantity_(converted)": 50,
                    "quantity": 10,
                    "reserves": -50,
                })
            elif sector == "methane plumes":
                co2_col = (self.find_column(df, {
                    "co2e": 20,
                    "emissions": 10,
                    "methane": 8
                }))
            elif sector in ["steel", "iron"]:
                co2_col = self.find_column(df, {
                    "nominal_crude_steel_capacity": 30,     # most specific first
                    "current_capacity": 20,
                    "capacity": 10,
                    "ttpa": 15,
                    "co2": 8,
                    "emission": 10,
                    "type_of_production": -50,
                    "production": -5,
                    "relining": -30,
                })

            has_emissions = co2_col is not None
            has_reserves = reserve_col is not None
            """terminal reporting"""
            if not has_emissions and not has_reserves:
                print(f"skipping {entry['sheet']} - no climate data")
                entry["cleaned_data"] = []
                continue                                    # Terminal report of failure, and a skip to the next sheet
            print(f"\n---------------Detected Columns in {entry['sheet']}:")
            print(f"\tname:\t\t{name_col}")
            if not name_col:
                print("MISSING: name_col")
            print(f"\tcountry:\t{country_col}")
            if not country_col:
                print("MISSING: country_col")
            print(f"\tyear:\t\t{year_col}")
            if not year_col:
                print("MISSING: year_col")
            print(f"\towner:\t\t{owner_col}")
            if co2_col:
                print(f"\tco2:\t\t{co2_col}")
            else:
                print("MISSING: co2_col")
            if reserve_col:
                print(f"\treserve:\t{reserve_col}")
            else:
                print("MISSING: reserve_col")

            for _, row in df.iterrows():                    # Looping through rows in filtered columns in spreadsheet, and organizing into "cleaned records"
                years = self.estimate_years_active(row.get(year_col))
                direct_total = None
                direct_annual = None
                potential_total = None
                potential_annual = None
                methane_annual = None

                valid_data = False
                if co2_col:
                    unit = self.infer_unit_from_column(co2_col) or row.get(unit_col)
                    val, dtype = self.normalize_value(row.get(co2_col), unit)
                    if val is not None:
                        valid_data = True
                        if dtype == "direct_total":
                            direct_total = val
                            if years:
                                direct_annual = val / years
                        elif dtype == "direct_annual":
                            direct_annual = val
                            if years:
                                direct_total = val * years
                        if sector == "methane plumes":
                            ch4_unit = self.infer_unit_from_column(co2_col, raw_ch4=True)
                            ch4_val, ch4_dtype = self.normalize_value(row.get(co2_col), ch4_unit)
                            if ch4_val is not None and ch4_dtype == "methane_annual":
                                methane_annual = ch4_val
                if reserve_col:
                    reserve_unit = self.infer_unit_from_column(reserve_col) or row.get(reserve_unit_col)
                    val, dtype = self.normalize_value(row.get(reserve_col), reserve_unit)
                    if val is not None:
                        valid_data = True
                        if dtype == "potential_total":
                            potential_total = val
                            if years:
                                potential_annual = val / years
                        elif dtype == "potential_annual":
                            potential_annual = val
                            if years:
                                potential_total = val * years
                if not valid_data:
                    continue
                cleaned_records.append({
                    "name": row.get(name_col) if name_col else None,
                    "country": row.get(country_col) if country_col else None,
                    "owner": row.get(owner_col) if owner_col else None,
                    "year": row.get(year_col) if year_col else None,
                    "sector": sector,

                    "direct_total": direct_total,
                    "direct_annual": direct_annual,
                    "potential_total": potential_total,
                    "potential_annual": potential_annual,
                    "methane_annual": methane_annual

                    #"fuel_type": row.get(fuel_col) if fuel_col else None,
                })

            entry["cleaned_data"] = cleaned_records

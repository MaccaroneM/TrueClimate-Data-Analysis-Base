#ANALYSISENGINE

#main class that does the interpretations of data from both viz and data helpers,
#generates verbiage for each sector, and stores it here. Basic math and logic will be done here,
#and sent to viz manager.

import math

class AnalysisEngine:
    def __init__(self, sheets):
        self.sheets = sheets
        self.results = {}
        self.cats = ["direct_total", "direct_annual", "potential_total", "potential_annual", "methane_annual"]
        pass

    def avg_emissions(self):
        """Finds the average emissions of each plant within the sector (sheet)"""
        for sheet in self.sheets:                                                   # Loops through sheets
            sector = sheet['sector']                                                # shortcut for going through sectors in sheets
            for record in sheet.get('cleaned_data', []):
                for key in self.cats:
                    val = record.get(key)
                    if (
                        isinstance(val, (int, float))
                        and not math.isnan(val)
                        and val != 0
                    ):
                        result_key = f"{key}_avg"
                        if result_key not in self.results:
                            self.results[result_key] = {}
                        if sector not in self.results[result_key]:
                            self.results[result_key][sector] = {"total": 0, "count": 0}
                        self.results[result_key][sector]["total"] += val
                        self.results[result_key][sector]["count"] += 1
        for key in self.results:
            if not key.endswith("_avg"):
                continue
            for sector in self.results[key]:
                data = self.results[key][sector]
                if isinstance(data, dict):
                    total = data["total"]
                    count = data["count"]
                    self.results[key][sector] = (
                        total / count if count > 0 else None
                    )
        return self.results
    def most_emissions_per_country_per_sector(self):
        """Calculates total emissions per country within each sector"""
        for sheet in self.sheets:
            sector = sheet["sector"]
            for record in sheet.get("cleaned_data", []):
                country = record.get("country")
                if not country:
                    continue
                for key in self.cats:
                    val = record.get(key)
                    if (
                        isinstance(val, (int, float))
                        and not math.isnan(val)
                        and val != 0
                    ):
                        result_key = f"{key}_country"
                        if result_key not in self.results:
                            self.results[result_key] = {}
                        if sector not in self.results[result_key]:
                            self.results[result_key][sector] = {}
                        sector_data = self.results[result_key][sector]
                        sector_data[country] = sector_data.get(country, 0) + val
        return self.results
    def plants_opened_since(self):
        """Counts the total # of plants opened since set years per sector"""
        thresholds = [2000, 2010, 2020]
        for year_cutoff in thresholds:
            result_key = (f"plants_since_{year_cutoff}")
            if result_key not in self.results:
                self.results[result_key] = {}
            for sheet in self.sheets:
                sector = sheet["sector"]
                if sector not in self.results[result_key]:
                    self.results[result_key][sector] = 0
                for record in sheet.get("cleaned_data", []):
                    year = record.get("year")
                    if not isinstance(year, (int, float)) or math.isnan(year):
                        continue
                    year = int(year)
                    if year >= year_cutoff:
                        self.results[result_key][sector] += 1
        return self.results

    """THINGS THAT I WANT TO CALCULATE
    - Average emissions of plant per sector                                     (DONE)
    - Country with most of X                                                    (DONE)    
    - Company with most of X                                                    
    - Total emissions of sectors                                                (DONE)
    - Total plants per sector - external research required to find in detail
    - Plants opened since 2020
    """
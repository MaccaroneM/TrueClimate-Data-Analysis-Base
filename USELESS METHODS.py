def estimate_potential_co2(self, reserve_amount, reserve_unit, fuel_type):
    """Converts reserve totals into an estimated potential MtCO2"""
    if reserve_amount is None:
        return None
    try:
        float(str(reserve_amount).replace(",", ""))
    except:
        return None
    if pd.isna(reserve_amount):
        return None
    unit = str(reserve_unit).lower()
    if "bbl" in unit:
        return reserve_amount * 0.43
    elif "m³" in unit or "m3" in unit:
        return reserve_amount * 0.0019
    elif "boe" in unit:
        return reserve_amount * 0.43
    # If the function cannot convert anything
    return None
"""def blah(self):
    if emissions_type == "cmm_20yr":
        lifetime = self.estimate_lifetime_from_cmm(val, row.get(year_col))
        if lifetime is not None:
            direct_total = lifetime
            direct_annual = val
        else:
            direct_annual = val
    else:
        if dtype == "direct_total":
            direct_total = val

            if check_float(row.get(year_col)):
                start_year = float(row.get(year_col))
                current_year = datetime.now().year
                years = current_year - start_year
                if years > 0:
                    direct_annual = val / years
        elif dtype == "direct_annual":
            direct_annual = val"""

"""direct_total = 0
    direct_count = 0
    total_potential_total = 0
    total_potential_count = 0
    annual_potential_total = 0
    annual_potential_count = 0
    for record in sheet.get('cleaned_data', []):                            # Loops through records in cleaned data
        data_type = record.get('data_type')
        if data_type == "direct_total" or data_type == "direct_annual":
            val = record.get('co2')
            if (
                isinstance(val, (int, float))
                and not math.isnan(val)
                and val != 0
            ):
                direct_total += val
                direct_count += 1
        elif data_type == "potential_total":
            val = record.get('potential_co2')
            if (
                isinstance(val, (int, float))
                and not math.isnan(val)
                and val != 0
            ):
                total_potential_total += val
                total_potential_count += 1
        elif data_type == "potential_annual":
            val = record.get('potential_co2')
            if (
                isinstance(val, (int, float))
                and not math.isnan(val)
                and val != 0
            ):
                annual_potential_total += val
                annual_potential_count += 1
    if sector not in self.results["direct_avg"]:
        self.results["direct_avg"][sector] = {"total": 0, "count": 0}       # Initializes a storage place in results
    if sector not in self.results["total_potential_avg"]:
        self.results["total_potential_avg"][sector] = {"total": 0, "count": 0}
    if sector not in self.results["annual_potential_avg"]:
        self.results["annual_potential_avg"][sector] = {"total": 0, "count": 0}
    self.results["direct_avg"][sector]["total"] += direct_total
    self.results["direct_avg"][sector]["count"] += direct_count
    self.results["total_potential_avg"][sector]["total"] += total_potential_total
    self.results["total_potential_avg"][sector]["count"] += total_potential_count
    self.results["annual_potential_avg"][sector]["total"] += annual_potential_total
    self.results["annual_potential_avg"][sector]["count"] += annual_potential_count
for sector, data in self.results["direct_avg"].items():                  # converts totals across sheets into averages
    direct = self.results["direct_avg"][sector]
    totpot = self.results["total_potential_avg"][sector]
    annpot = self.results["annual_potential_avg"][sector]
    self.results["direct_avg"][sector] = (
        direct["total"] / direct["count"] if direct["count"] > 0 else None
    )
    self.results["total_potential_avg"][sector] = (
        totpot["total"] / totpot["count"] if totpot["count"] > 0 else None
    )
    self.results["annual_potential_avg"][sector] = (
        annpot["total"] / annpot["count"] if annpot["count"] > 0 else None
    )
return self.results    """  # function returns value

"""if sector not in self.results["direct_country_totals"]:                 # checks to see if sector available, and creates it
        self.results["direct_country_totals"][sector] = {}
    if sector not in self.results["total_potential_country_totals"]:
        self.results["total_potential_country_totals"][sector] = {}
    if sector not in self.results["annual_potential_country_totals"]:
        self.results["annual_potential_country_totals"][sector] = {}
    for record in sheet.get('cleaned_data', []):
        country = record.get('country')                                     # Country shortcut in Dictionary
        if not country:
            continue
        data_type = record.get('data_type')
        if data_type == "direct_total":
            val = record.get('co2')
            if (
                isinstance(val, (int, float))
                and not math.isnan(val)
                and val != 0
            ):
                sector_data = self.results["direct_country_totals"][sector]
                sector_data[country] = sector_data.get(country, 0) + val
        elif data_type == "potential_total":
            val = record.get('potential_co2')
            if (
                isinstance(val, (int, float))
                and not math.isnan(val)
                and val != 0
            ):
                sector_data = self.results["total_potential_country_totals"][sector]
                sector_data[country] = sector_data.get(country, 0) + val
        elif data_type == "potential_annual":
            val = record.get('potential_co2')
            if (
                isinstance(val, (int, float))
                and not math.isnan(val)
                and val != 0
            ):
                sector_data = self.results["annual_potential_country_totals"][sector]
                sector_data[country] = sector_data.get(country, 0) + val"""


"""def estimate_lifetime_from_cmm(self, cmm_value, opening_year):
    if not check_float(opening_year):
        return None
    if not check_float(cmm_value):
        return None
    opening_year = float(opening_year)
    cmm_value = float(cmm_value)
    if pd.isna(opening_year) or pd.isna(cmm_value):
        return None
    current_year = datetime.now().year
    years_active = current_year - opening_year
    if years_active <= 0:
        return None
    return cmm_value * years_active"""


def normalize_potential(self, amount, unit):
    if not check_float(amount):
        return None, None
    amount = float(amount)
    unit = str(unit).lower()
    is_annual = "/y" in unit or "per year" in unit
    if "bbl" in unit or "boe" in unit:
        co2 = amount * 0.43
    elif "m³" in unit or "m3" in unit:
        co2 = amount * 0.0019
    else:
        return None, None
    dtype = "potential_annual" if is_annual else "potential_total"
    return co2, dtype

def normalize_direct(self, value, unit):
    if not check_float(value):
        return None, None
    value = float(value)
    unit = str(unit).lower() if unit else ""
    if "kg/hr" in unit:
        annual_kg = value * 24 * 365
        return annual_kg / 1e9, "direct_annual"
    return value, "direct_total"

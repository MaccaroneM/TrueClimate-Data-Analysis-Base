#TESTING

from analysisengine import AnalysisEngine
from datamanager import DataManager
import math
if __name__ == "__main__":
    # ------------------------
    # DATA SETUP & CLEANING
    # ------------------------
    dm = DataManager()

    dm.load_energy_monitor_data()
    print(f"\nLoaded {len(dm.sheets)} sheets\n")

    dm.clean_data()

    print("\n---{SAMPLE CLEANED DATA}---")

    for entry in dm.sheets[:2]:
        print(f"\nREADING: {entry['sheet']}")
        for record in entry.get("cleaned_data", [])[:5]:
            print(record)

    # ------------------------
    # DATA COMPLETENESS CHECK
    # ------------------------
    counts = {
        "direct_total": 0,
        "direct_annual": 0,
        "potential_total": 0,
        "potential_annual": 0
    }

    total_records = 0

    for entry in dm.sheets:
        for r in entry.get("cleaned_data", []):
            total_records += 1
            for key in counts:
                val = r.get(key)
                if isinstance(val, (int, float)) and not math.isnan(val) and val != 0:
                    counts[key] += 1

    print("\n---{DATA COVERAGE}---")
    print(f"Total records: {total_records}")
    for key, val in counts.items():
        print(f"{key}: {val}")

    # ------------------------
    # SHEET BREAKDOWN
    # ------------------------
    print("\n---{SHEET BREAKDOWN}---")
    for entry in dm.sheets:
        print(
            entry["sheet"],
            "| sector:", entry["sector"],
            "| rows:", len(entry.get("cleaned_data", []))
        )

    # ------------------------
    # DATA ANALYSIS
    # ------------------------
    ae = AnalysisEngine(dm.sheets)

    ae.avg_emissions()
    ae.most_emissions_per_country_per_sector()
    ae.plants_opened_since()

    print("\n---{ANALYSIS RESULTS}---\n")

    # ------------------------
    # AVERAGES
    # ------------------------
    def print_avg(title, key):
        print(title)
        dataset = ae.results.get(key, {})
        for sector, val in dataset.items():
            if val:
                print(f"  {sector}: {val:,.2f}")
            else:
                print(f"  {sector}: No data")
        print()

    print_avg("Average Emissions per Sector (DIRECT TOTAL):", "direct_total_avg")
    print_avg("Average Emissions per Sector (DIRECT ANNUAL):", "direct_annual_avg")
    print_avg("Average Emissions per Sector (POTENTIAL TOTAL):", "potential_total_avg")
    print_avg("Average Emissions per Sector (POTENTIAL ANNUAL):", "potential_annual_avg")
    print_avg("Average Emissions per Sector (RAW CH4, ANNUAL):", "methane_annual_avg")

    print("\n------------------------\n")

    # ------------------------
    # TOP COUNTRIES
    # ------------------------
    def print_top(title, key):
        print(title)
        dataset = ae.results.get(key, {})

        for sector, countries in dataset.items():
            print(f"\n  Sector: {sector}")

            sorted_countries = sorted(
                countries.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for country, val in sorted_countries[:5]:
                print(f"    {country}: {val:,.0f}")
        print()

    print_top("Top Countries (DIRECT TOTAL):", "direct_total_country")
    print_top("Top Countries (DIRECT ANNUAL):", "direct_annual_country")
    print_top("Top Countries (POTENTIAL TOTAL):", "potential_total_country")
    print_top("Top Countries (POTENTIAL ANNUAL):", "potential_annual_country")
    print_top("Top Countries (METHANE ANNUAL RAW):", "methane_annual_country")

    print("\n------------------------\n")

    # ------------------------
    # TOTALS
    # ------------------------
    def print_totals(title, key):
        print(title)
        dataset = ae.results.get(key, {})

        for sector, countries in dataset.items():
            total = sum(countries.values())
            if total:
                print(f"  {sector}: {total:,.0f}")
            else:
                print(f"  {sector}: No data")
        print()

    print_totals("Total Emissions per Sector (DIRECT TOTAL):", "direct_total_country")
    print_totals("Total Emissions per Sector (DIRECT ANNUAL):", "direct_annual_country")
    print_totals("Total Emissions per Sector (POTENTIAL TOTAL):", "potential_total_country")
    print_totals("Total Emissions per Sector (POTENTIAL ANNUAL):", "potential_annual_country")
    print_totals("Total Methane per Sector (ANNUAL RAW):", "methane_annual_country")

    print("\n------------------------\n")


    def print_counts(title, key):
        print(title)
        dataset = ae.results.get(key, {})
        for sector, count in dataset.items():
            print(f"  {sector}: {count}")
        print()


    print_counts("Plants opened since 2000:", "plants_since_2000")
    print_counts("Plants opened since 2010:", "plants_since_2010")
    print_counts("Plants opened since 2020:", "plants_since_2020")

    from vizmanager import VizManager

    vm = VizManager(ae.results)

    # Example runs
    vm.create_sector_visual("coal plants", "direct_total_country")
    vm.create_sector_visual("iron", "direct_total_country")
    vm.create_sector_visual("oil and gas extraction", "potential_total_country")
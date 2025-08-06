"""
Zentrale Stelle für statische Testdaten.
- `test_cache_data`: Füllt die Auswahl-Dialoge.
- `db_connections_data`: Definiert Standard-Schemas.
- `dependencies`: Definiert das eigentliche Data Lineage für die Graphen.
"""

# 1. Daten für die Auswahl-Dialoge
test_cache_data = {
    "PROD_DATABASE": {
        "DWH_CORE": {
            "TABLE": ["F_SALES_TRANSACTIONS", "F_INVENTORY_LEVELS", "D_CUSTOMER", "D_PRODUCT"],
            "VIEW": ["V_SALES_AGG_MONTHLY", "V_CUSTOMER_SEGMENTATION"],
            "ELT": ["ELT_LOAD_DWH_CORE"]
        },
        "REPORTING": {
            "TABLE": [],
            "VIEW": ["V_CEO_DASHBOARD", "V_QUARTERLY_SALES"],
            "ELT": ["ELT_LOAD_REPORTS"]
        },
        "STAGING": {
            "TABLE": ["RAW_POS_DATA", "RAW_SHIPMENT_LOGS", "RAW_CUSTOMER_DATA"],
            "VIEW": [],
            "ELT": ["ELT_LOAD_STAGING"]
        },
    },
    "DEV_DATABASE": {
        "SANDBOX_MIKA": {
            "TABLE": ["TEMP_CUSTOMER_ANALYSIS"],
            "VIEW": ["V_MIKA_TEST_AGGREGATE"],
            "ELT": ["MIKA_TEST_ELT_01", "MIKA_FEATURE_BRANCH_REPORT"]
        }
    }
}

# 2. Metadaten für DB-Verbindungen
db_connections_data = {
    "PROD_DATABASE": {"schemas": {"default_schema": "REPORTING"}},
    "DEV_DATABASE": {"schemas": {"default_schema": "SANDBOX_MIKA"}},
}

# 3. Definition der Abhängigkeiten (Data Lineage)
# Hier wird die Logik für die Graphenerzeugung gesteuert.
dependencies = {
    # Staging-Prozesse
    "ELT_LOAD_STAGING": {
        "inputs": ["LEGACY_SYSTEM_DB.dbo.KUNDENSTAMM_ALT", "LEGACY_SYSTEM_DB.dbo.AUFTRAEGE_2010_2015"],
        "outputs": ["STAGING.RAW_CUSTOMER_DATA", "STAGING.RAW_POS_DATA", "STAGING.RAW_SHIPMENT_LOGS"]
    },

    # DWH-Core-Prozesse
    "ELT_LOAD_DWH_CORE": {
        "inputs": ["STAGING.RAW_POS_DATA", "STAGING.RAW_SHIPMENT_LOGS", "STAGING.RAW_CUSTOMER_DATA"],
        "outputs": ["DWH_CORE.F_SALES_TRANSACTIONS", "DWH_CORE.F_INVENTORY_LEVELS", "DWH_CORE.D_CUSTOMER", "DWH_CORE.D_PRODUCT"]
    },
    "V_SALES_AGG_MONTHLY": ["DWH_CORE.F_SALES_TRANSACTIONS", "DWH_CORE.D_PRODUCT"],
    "V_CUSTOMER_SEGMENTATION": ["DWH_CORE.D_CUSTOMER", "DWH_CORE.F_SALES_TRANSACTIONS"],

    # Reporting-Prozesse
    "ELT_LOAD_REPORTS": {
        "inputs": ["DWH_CORE.V_SALES_AGG_MONTHLY", "DWH_CORE.V_CUSTOMER_SEGMENTATION"],
        "outputs": ["REPORTING.V_QUARTERLY_SALES"]
    },
    "V_CEO_DASHBOARD": ["REPORTING.V_QUARTERLY_SALES", "DWH_CORE.F_INVENTORY_LEVELS"],

    # Dev-Prozesse
    "MIKA_TEST_ELT_01": {
        "inputs": ["DWH_CORE.D_CUSTOMER"],
        "outputs": ["SANDBOX_MIKA.TEMP_CUSTOMER_ANALYSIS"]
    },
    "V_MIKA_TEST_AGGREGATE": ["SANDBOX_MIKA.TEMP_CUSTOMER_ANALYSIS"]
}
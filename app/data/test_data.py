"""
Zentrale Stelle für statische Testdaten.
- `test_cache_data`: Füllt die Auswahl-Dialoge.
- `db_connections_data`: Definiert Standard-Schemas.
- `dependencies`: Definiert das eigentliche Data Lineage für die Graphen.
"""

# 1. Daten für die Auswahl-Dialoge (inkl. der neuen Artefakte für den Riesengraphen)
test_cache_data = {
    "PROD_DATABASE": {
        "DWH_CORE": {
            "TABLE": ["F_SALES_TRANSACTIONS", "F_INVENTORY_LEVELS", "D_CUSTOMER", "D_PRODUCT"],
            "VIEW": ["V_SALES_AGG_MONTHLY", "V_CUSTOMER_SEGMENTATION"],
            "ELT": ["ELT_LOAD_DWH_CORE"]
        },
        "REPORTING": {
            "TABLE": [],
            "VIEW": [
                "V_CEO_DASHBOARD",
                "V_QUARTERLY_SALES",
                # Artefakte für den Riesengraphen
                "V_AGG_CUSTOMER_LIFETIME_VALUE",
                "V_AGG_OPERATIONAL_COSTS",
                "V_AGG_PRODUCT_PROFITABILITY",
                "V_AGG_REVENUE_BY_REGION",
                "V_COMPREHENSIVE_FINANCE_REPORT"  # Dies ist der Einstiegspunkt für den Riesengraphen
            ],
            "ELT": ["ELT_LOAD_REPORTS"]
        },
        "STAGING": {
            "TABLE": [
                "RAW_POS_DATA",
                "RAW_SHIPMENT_LOGS",
                "RAW_CUSTOMER_DATA",
                # Neue Tabellen für den Riesengraphen
                "RAW_FACILITIES_RENT",
                "RAW_HR_SALARIES",
                "RAW_INVENTORY_DATA",
                "RAW_IT_EXPENSES",
                "RAW_MARKETING_SPEND",
                "RAW_SUPPLY_CHAIN_COSTS"
            ],
            "VIEW": [],
            "ELT": [
                "ELT_LOAD_STAGING", # Ursprünglicher, einfacher Prozess
                # Neue, detaillierte Prozesse für den Riesengraphen
                "ELT_LOAD_STAGING_CRM",
                "ELT_LOAD_STAGING_FINANCE",
                "ELT_LOAD_STAGING_HR",
                "ELT_LOAD_STAGING_LOGISTICS",
                "ELT_LOAD_STAGING_MARKETING",
                "ELT_LOAD_STAGING_RETAIL",
                "ELT_LOAD_STAGING_SUPPLY_CHAIN"
            ]
        },
    },
    "DEV_DATABASE": {
        "SANDBOX_MIKA": {
            "TABLE": ["TEMP_CUSTOMER_ANALYSIS", "TEMP_ANALYSIS_RESULTS"],
            "VIEW": ["V_MIKA_TEST_AGGREGATE", "V_MIKA_JOINED_DATA"],
            "ELT": ["MIKA_TEST_ELT_01", "MIKA_FEATURE_BRANCH_REPORT", "MIKA_PROCESS_INTERMEDIATE"]
        }
    }
}

# 2. Metadaten für DB-Verbindungen
db_connections_data = {
    "PROD_DATABASE": {"schemas": {"default_schema": "REPORTING"}},
    "DEV_DATABASE": {"schemas": {"default_schema": "SANDBOX_MIKA"}},
}

# 3. Definition der Abhängigkeiten (Data Lineage)
dependencies = {
    # Staging-Prozesse (einfach)
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

    # Reporting-Prozesse (einfach)
    "ELT_LOAD_REPORTS": {
        "inputs": ["DWH_CORE.V_SALES_AGG_MONTHLY", "DWH_CORE.V_CUSTOMER_SEGMENTATION"],
        "outputs": ["REPORTING.V_QUARTERLY_SALES"]
    },
    "V_CEO_DASHBOARD": ["REPORTING.V_QUARTERLY_SALES", "DWH_CORE.F_INVENTORY_LEVELS"],

    # Dev-Prozesse
    "MIKA_TEST_ELT_01": {
        "inputs": ["DWH_CORE.D_CUSTOMER", "DWH_CORE.F_SALES_TRANSACTIONS"],
        "outputs": ["SANDBOX_MIKA.TEMP_CUSTOMER_ANALYSIS"]
    },
    "MIKA_PROCESS_INTERMEDIATE": {
        "inputs": ["SANDBOX_MIKA.TEMP_CUSTOMER_ANALYSIS"],
        "outputs": ["SANDBOX_MIKA.TEMP_ANALYSIS_RESULTS"]
    },
    "V_MIKA_JOINED_DATA": ["SANDBOX_MIKA.TEMP_ANALYSIS_RESULTS", "DWH_CORE.D_PRODUCT"],
    "V_MIKA_TEST_AGGREGATE": ["SANDBOX_MIKA.V_MIKA_JOINED_DATA"],

    # === BEGINN DES RIESENGRAPHEN ===

    # Ebene 1: Finaler Report (Einstiegspunkt)
    # Hängt von 4 Haupt-Aggregations-Views ab
    "V_COMPREHENSIVE_FINANCE_REPORT": [
        "REPORTING.V_AGG_REVENUE_BY_REGION",
        "REPORTING.V_AGG_PRODUCT_PROFITABILITY",
        "REPORTING.V_AGG_CUSTOMER_LIFETIME_VALUE",
        "REPORTING.V_AGG_OPERATIONAL_COSTS"
    ],

    # Ebene 2: Jeder Aggregations-View wird aus verschiedenen Quellen gebaut
    "REPORTING.V_AGG_REVENUE_BY_REGION": ["DWH_CORE.F_SALES_TRANSACTIONS", "DWH_CORE.D_CUSTOMER", "DWH_CORE.D_PRODUCT"],
    "REPORTING.V_AGG_PRODUCT_PROFITABILITY": ["DWH_CORE.F_SALES_TRANSACTIONS", "DWH_CORE.D_PRODUCT", "STAGING.RAW_SUPPLY_CHAIN_COSTS"],
    "REPORTING.V_AGG_CUSTOMER_LIFETIME_VALUE": ["DWH_CORE.F_SALES_TRANSACTIONS", "DWH_CORE.D_CUSTOMER", "STAGING.RAW_MARKETING_SPEND"],
    "REPORTING.V_AGG_OPERATIONAL_COSTS": ["STAGING.RAW_HR_SALARIES", "STAGING.RAW_FACILITIES_RENT", "STAGING.RAW_IT_EXPENSES"],

    # Ebene 3: Detaillierte Staging-Prozesse, die die Rohdaten laden
    "ELT_LOAD_STAGING_RETAIL": {
        "inputs": ["SOURCE_SYSTEMS.RETAIL_POS_SYSTEM.dbo.SALES", "SOURCE_SYSTEMS.RETAIL_POS_SYSTEM.dbo.RETURNS"],
        "outputs": ["STAGING.RAW_POS_DATA"]
    },
    "ELT_LOAD_STAGING_LOGISTICS": {
        "inputs": ["SOURCE_SYSTEMS.LOGISTICS_API.v1.SHIPMENTS", "SOURCE_SYSTEMS.WAREHOUSE_DB.wms.STOCK_LEVELS"],
        "outputs": ["STAGING.RAW_SHIPMENT_LOGS", "STAGING.RAW_INVENTORY_DATA"]
    },
    "ELT_LOAD_STAGING_CRM": {
        "inputs": ["SOURCE_SYSTEMS.CRM_SALESFORCE.api.ACCOUNTS", "SOURCE_SYSTEMS.CRM_SALESFORCE.api.CONTACTS"],
        "outputs": ["STAGING.RAW_CUSTOMER_DATA"]
    },
    "ELT_LOAD_STAGING_SUPPLY_CHAIN": {
        "inputs": ["SOURCE_SYSTEMS.SAP_ERP.fi.CO_PA_DATA"],
        "outputs": ["STAGING.RAW_SUPPLY_CHAIN_COSTS"]
    },
    "ELT_LOAD_STAGING_MARKETING": {
        "inputs": ["SOURCE_SYSTEMS.GOOGLE_ADS.api.CAMPAIGN_SPEND", "SOURCE_SYSTEMS.FACEBOOK_ADS.api.PERFORMANCE"],
        "outputs": ["STAGING.RAW_MARKETING_SPEND"]
    },
    "ELT_LOAD_STAGING_HR": {
        "inputs": ["SOURCE_SYSTEMS.WORKDAY_HR.reports.PAYROLL_EXPORT"],
        "outputs": ["STAGING.RAW_HR_SALARIES"]
    },
    "ELT_LOAD_STAGING_FINANCE": {
        "inputs": ["SOURCE_SYSTEMS.FINANCE_DB.gl.GENERAL_LEDGER"],
        "outputs": ["STAGING.RAW_FACILITIES_RENT", "STAGING.RAW_IT_EXPENSES"]
    }
    # === ENDE DES RIESENGRAPHEN ===
}
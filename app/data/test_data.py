"""
Zentrale Stelle für statische Testdaten im verschachtelten Format,
das vom komplexen Auswahl-Dialog erwartet wird.
Diese Datei simuliert einen Cache von Datenbank-Metadaten.
"""

# 1. Die Haupt-Datenstruktur, die den Cache simuliert
# Format: { "Datenquelle": { "Schema": { "Artefakt-Listen" } } }
test_cache_data = {
    "PROD_DATABASE": {
        "DWH_CORE": {
            "unique_artifacts": [],
            "unique_tables": [
                {"table_name": "F_SALES_TRANSACTIONS", "table_object_id": 1001},
                {"table_name": "F_INVENTORY_LEVELS", "table_object_id": 1002},
                {"table_name": "D_CUSTOMER", "table_object_id": 2001},
                {"table_name": "D_PRODUCT", "table_object_id": 2002},
            ],
            "unique_views": [
                {"view_name": "V_SALES_AGG_MONTHLY", "view_object_id": 3001},
            ],
        },
        "REPORTING": {
            "unique_artifacts": ["CEO_FINANCE_DASHBOARD", "QUARTERLY_SALES_REPORT"],
            "unique_tables": [],
            "unique_views": [
                {"view_name": "V_AGG_SALES_MONTHLY", "view_object_id": 3001},
                {"view_name": "V_CUSTOMER_SEGMENTATION", "view_object_id": 3002},
            ],
        },
        "STAGING": {
            "unique_artifacts": [],
            "unique_tables": [
                {"table_name": "RAW_POS_DATA", "table_object_id": 9001},
                {"table_name": "RAW_SHIPMENT_LOGS", "table_object_id": 9002},
            ],
            "unique_views": [],
        },
    },
    "DEV_DATABASE": {
        "SANDBOX_MIKA": {
            "unique_artifacts": ["MIKA_TEST_ELT_01", "MIKA_FEATURE_BRANCH_REPORT"],
            "unique_tables": [
                {"table_name": "TEMP_CUSTOMER_ANALYSIS", "table_object_id": 7101},
            ],
            "unique_views": [
                {"view_name": "V_MIKA_TEST_AGGREGATE", "view_object_id": 8101},
            ],
        },
        "SANDBOX_SHARED": {
            "unique_artifacts": ["SHARED_TEST_PROCEDURE"],
            "unique_tables": [],
            "unique_views": [],
        },
    },
    "LEGACY_SYSTEM_DB": {
        "dbo": {
            "unique_artifacts": [],
            "unique_tables": [
                {"table_name": "KUNDENSTAMM_ALT", "table_object_id": 5001},
                {"table_name": "AUFTRAEGE_2010_2015", "table_object_id": 5002},
            ],
            "unique_views": [],
        }
    }
}


# 2. Zusätzliche Metadaten zu den "DB-Verbindungen"
# Wird vom Dialog verwendet, um z.B. das Standard-Schema vorzuschlagen.
db_connections_data = {
    "PROD_DATABASE": {
        "schemas": {
            "default_schema": "REPORTING"
        }
    },
    "DEV_DATABASE": {
        "schemas": {
            "default_schema": "SANDBOX_MIKA"
        }
    },
    "LEGACY_SYSTEM_DB": {
         "schemas": {
            "default_schema": "dbo"
        }
    }
}
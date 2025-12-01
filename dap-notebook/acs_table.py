

# -----------------------------------------------
# Base ACS class (equiv. to sealed trait ACS)
# -----------------------------------------------

class ACS:
    table_name: str
    table_type: str
    description: str

    def full_name(self):
        return AcsResolver.get_name(self)

    def __str__(self):
        return self.full_name()

    def __repr__(self):
        return self.full_name()



# -----------------------------------------------
# ACS Table Definitions (equiv. to case objects)
# -----------------------------------------------

class DAlmaOpenAccess(ACS):
    table_name = "d_alma_openaccess"
    table_type = "entity"
    description = "Alma Open Access Data"


class DAlmaSubscriptions(ACS):
    table_name = "d_alma_subscriptions"
    table_type = "entity"
    description = "Alma Subscriptions Data"


class DEsiAuthor(ACS):
    table_name = "d_esi_author"
    table_type = "entity"
    description = "ESI Author Data"


class DEsiCountry(ACS):
    table_name = "d_esi_country"
    table_type = "entity"
    description = "ESI Country Data"


class DEsiInstitution(ACS):
    table_name = "d_esi_institution"
    table_type = "entity"
    description = "ESI Institution Data"



# -----------------------------------------------
# AcsResolver (equivalent to Scala object)
# -----------------------------------------------

class AcsResolver:
    @staticmethod
    def _get_widget(name: str, default: str):
        try:
            value = dbutils.widgets.get(name)
            return value if value else default
        except Exception:
            return default

    # Read widgets (same as Scala)
    environment = _get_widget.__func__("environment", "dev")
    version     = _get_widget.__func__("version", "v1_0")
    collection  = _get_widget.__func__("collection", "wos")

    catalog = f"ag_ra_search_analytics_data_{environment}"

    dataset_suffix = ""

    @classmethod
    def set_dataset(cls, dataset=""):
        cls.dataset_suffix = "_woscore" if dataset == "woscore" else ""

    @classmethod
    def get_name(cls, table: ACS):
        if table.table_type == "entity":
            return f"{cls.catalog}.gold_entity_{cls.version}.{table.table_name}"

        elif table.table_type == "collection":
            return f"{cls.catalog}.gold_{cls.collection}_{cls.version}.{table.table_name}"

        elif table.table_type == "dataset":
            return (
                f"{cls.catalog}.gold_{cls.collection}_{cls.version}"
                f".{table.table_name}{cls.dataset_suffix}"
            )

        else:
            raise ValueError(f"Unknown table_type: {table.table_type}")



# Usage Examples (Same as Scala)
print(DAlmaOpenAccess())

# ag_ra_search_analytics_data_dev.gold_entity_v1_0.d_alma_openaccess

# With dataset enabled (equivalent to Scala setDataset("woscore"))

AcsResolver.set_dataset("woscore")
print(DEsiAuthor())

# ag_ra_search_analytics_data_dev.gold_entity_v1_0.d_esi_author_woscore

from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI(
    title="CRM Вектор",
    description="CRM Вектор API",
    urls_namespace="crm",
)
api.auto_discover_controllers()

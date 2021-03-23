from sundayleagueApp.models import SystemSetting


# Get value from systemSetting by key
def get_value(key):
    return SystemSetting.objects.get(key=key).string_value


# Check if value is equal to true
def get_bool_value(key):
    return get_value(key).lower() == "true"


# Save value to systemSetting
def save(key, value):
    system_setting = SystemSetting.objects.get(key=key) if SystemSetting.objects.get(key=key) else SystemSetting(
        key=key, value=value)
    system_setting.string_value = value
    system_setting.save()

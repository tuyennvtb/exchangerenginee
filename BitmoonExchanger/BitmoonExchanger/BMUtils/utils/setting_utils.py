from ...BMExchanger.models import ExchangerAdminSetting
from .constants import *
class SettingUtils:
    @classmethod
    def get_setting(cls,key,default_value,description):
        setting = None
        try:
            setting = ExchangerAdminSetting.objects.filter(setting_name=key).get()
            return setting.setting_number_value
        except:    
            #Setting not found
            try:
                setting = ExchangerAdminSetting()
                setting.setting_name=key
                setting.setting_number_value = default_value
                setting.setting_text_value=description
                setting.save()
            except Exception as e:                
                
                pass
        
        if setting is None:
            return default_value
        else:
            return setting.setting_number_value


    @classmethod
    def get_usd_rate_vnd(cls):
        default_value = 23000

        vnd_rate = cls.get_setting(key=AdminSettingConstants.USD_RATE_VND,default_value=default_value,description='Ti gia USD')
        if vnd_rate < 20000:
            vnd_rate = default_value

        return float(vnd_rate)

    @classmethod
    def get_user_trading_fee(cls,custom_fee):
        default_value = 0.35

        fee = cls.get_setting(key=AdminSettingConstants.USER_TRADING_FEE,default_value=default_value,description='Phi giao dich cua khach hang. Vi du 0.35 percent')
        if fee < 0 or fee > default_value:
            fee = default_value

        if custom_fee >= 0 and custom_fee <= fee:
            fee = custom_fee

        return fee

    @classmethod
    def get_auto_cancel_value(cls):
        default_value = 20.0
        value = cls.get_setting(key=AdminSettingConstants.AUTO_CANCEL_VALUE,default_value=default_value,description='Giao dich se tu dong cancel neu thanh phan con lai it hon gia tri nay. Tinh bang $')
        if value < 0 or value > default_value:
            value = default_value

        return value

    @classmethod
    def enable_withdraw(cls):
        default_value=1
        value = cls.get_setting(key=AdminSettingConstants.ENABLE_WITHDRAW,default_value=default_value,description='Co cho phep withdraw khong ? ')

        return value

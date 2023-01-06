from django.db import models

# Create your models here.
class ExchangerAdminSetting(models.Model):
    ID = models.AutoField(primary_key=True)
    setting_name = models.CharField(max_length=100, null=False,unique=True)
    setting_number_value = models.DecimalField(null=False, max_digits=29, decimal_places=19,default=1) 
    setting_text_value = models.CharField(max_length=100, null=False,default='Unknown')

    class Meta:
        db_table = "exchanger_admin_setting"

# Create your models here.
class ExchangerCoinSetting(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    coin_id = models.CharField(max_length=100, null=False,unique=True)
    coin_name = models.CharField(max_length=100, null=False,default='Unknown')
    coin_symbol = models.CharField(max_length=100, null=True)

    client_buy_profit = models.DecimalField(null=True, max_digits=5, decimal_places=2,default=1) 
    client_sell_profit = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=1)


    created_at = models.DateTimeField(null=True, db_index=True)
    updated_at = models.DateTimeField(null=True, db_index=True)

    status = models.IntegerField(default=0,null=True)
    coin_group = models.IntegerField(default=0,null=True)

    is_allow_market_trade = models.IntegerField(default=0)
    is_allow_limit_trade = models.IntegerField(default=1)

    default_withdraw_network = models.CharField(max_length=100, null=True, default='')

    class Meta:
        db_table = "exchanger_coin_setting"


class ExchangerCoinGroupSetting(models.Model):
    ID = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=100, null=False,default='Unknown')
    broker_id = models.CharField(max_length=100, null=True,db_index=True)

    client_buy_profit = models.DecimalField(null=True, max_digits=5, decimal_places=2,default=1) 
    client_sell_profit = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=1)

    created_at = models.DateTimeField(null=True, db_index=True)
    updated_at = models.DateTimeField(null=True, db_index=True)

    is_allow_market_trade = models.IntegerField(default=0)
    is_allow_limit_trade = models.IntegerField(default=1)

    coin_status = models.IntegerField(default=0,null=True)

    class Meta:
        db_table = "exchanger_coin_groups"


# Create your models here.
class ExchangerCoinPriceModel(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    coin_id = models.CharField(max_length=100, null=False,unique=True)

    coin_name = models.CharField(max_length=100, null=False,default='Unknown')
    coin_symbol = models.CharField(max_length=100, null=False)

    usd_bid_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    usd_ask_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)

    vnd_bid_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    vnd_ask_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)

    usd_rate_vnd =  models.IntegerField(default=0,null=True)
    client_buy_profit = models.DecimalField(null=True, max_digits=5, decimal_places=2,default=1) 
    client_sell_profit = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=1)


    created_at = models.DateTimeField(null=True, db_index=True)
    updated_at = models.DateTimeField(null=True, db_index=True)

    status = models.IntegerField(default=0,null=False)

    class Meta:
        db_table = "exchanger_coin_price"
        
class ExchangerTransaction(models.Model):
    ID = models.AutoField(primary_key=True)
    user_id =  models.IntegerField(default=0,null=False)
    action =  models.CharField(max_length=100, null=False)
    trade_mode =  models.CharField(max_length=100, null=False)
    unique_id = models.CharField(max_length=100, null=False,unique=True)
    coin_id =  models.CharField(max_length=100, null=False)
    base_currency = models.CharField(max_length=100, null=False)
    coin_amount_submitted = models.DecimalField(null=False, max_digits=29, decimal_places=19) 
    coin_amount_filled = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    market_total_amount_submitted = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    market_total_amount_filled = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    reserved_amount = models.DecimalField(null=False, max_digits=29, decimal_places=19)
    reserved_remainings = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    submitted_price_vnd = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    price_vnd_when_submit = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    avg_price_usd = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    avg_price_vnd = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    estimate_vnd_amount = models.DecimalField(null=True, max_digits=29, decimal_places=9)
    fee_percent = models.DecimalField(null=True, max_digits=5, decimal_places=2,default=1)
    fee_reserved = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    total_final_fee = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    fee_refund = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    cost_amount = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    cost_amount_after_fee = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    final_money_added = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    refund_amount = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)

    wallet_payload = models.TextField()
    wallet_status = models.IntegerField(default=0,null=True)
    wallet_response = models.TextField()
    wallet_request_count = models.IntegerField(default=0,null=True)

    display_status = models.CharField(max_length=100, null=False)
    system_status = models.CharField(max_length=100, null=False,db_index=True)

    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    class Meta:
        db_table = "exchanger_transaction"

class ExchangerTransactionStepLimit(models.Model):
    ID = models.AutoField(primary_key=True)
    transaction_id =  models.IntegerField(default=0,null=False)
    user_id =  models.IntegerField(default=0,null=False)
    action =  models.CharField(max_length=100, null=False)
    trade_mode =  models.CharField(max_length=100, null=False)
    market_pair =  models.CharField(max_length=100, null=False)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    broker_unique_id = models.CharField(max_length=100, null=False,unique=False)
    coin_amount_submitted = models.DecimalField(null=False, max_digits=29, decimal_places=19) 
    coin_amount_filled = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    coin_amount_remainings = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    submitted_price = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    vnd_match_price = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    usd_rate_vnd = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    final_btc_price = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    final_usd_price = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    temp_vnd_price = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    final_vnd_price = models.DecimalField(null=True, max_digits=29, decimal_places=19)

    coin_fee = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    total_fee = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    cost_amount = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    cost_amount_after_fee = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    final_money_added = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    wallet_payload = models.TextField()
    wallet_status = models.IntegerField(default=0,null=True)
    wallet_response = models.TextField()
    wallet_request_count = models.IntegerField(default=0,null=True)

    fulfillment_broker_unique_id = models.CharField(max_length=100, null=True,unique=False)

    system_status = models.CharField(max_length=100, null=False,db_index=True)

    class Meta:
        db_table = "exchanger_transaction_step_limit"

class ExchangerTransactionStepTrading(models.Model):
    ID = models.AutoField(primary_key=True)
    coin_id =  models.CharField(max_length=100, null=False)
    buy_id  = models.IntegerField(default=0,null=False,db_index=True)
    sell_id = models.IntegerField(default=0,null=False,db_index=True)
    buy_user_id =  models.IntegerField(default=0,null=False)
    sell_user_id =  models.IntegerField(default=0,null=False)
    unique_id = models.CharField(max_length=100, unique=True)
    leading_action = models.CharField(max_length=100, null=False)
    coin_amount = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    final_vnd_price = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    buy_fee_percent = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    buy_fee = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    sell_fee_percent = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    sell_fee = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    exchanger_total_fee = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    cost_amount = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    cost_amount_after_fee_buy = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    cost_amount_after_fee_sell = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    final_money_added_buy = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    final_money_added_sell = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    
    wallet_buy_payload = models.TextField(default='')
    wallet_buy_status = models.IntegerField(default=0,null=True)
    wallet_buy_response = models.TextField(default='')
    wallet_buy_request_count = models.IntegerField(default=0,null=True)

    wallet_sell_payload = models.TextField(default='')
    wallet_sell_status = models.IntegerField(default=0,null=True)
    wallet_sell_response = models.TextField(default='')
    wallet_sell_request_count = models.IntegerField(default=0,null=True)

    

    system_status = models.CharField(max_length=100, null=False,db_index=True)

    class Meta:
        db_table = "exchanger_transaction_step_trading"

class ExchangerTransactionStepMarket(models.Model):
    ID = models.AutoField(primary_key=True)
    transaction_id =  models.IntegerField(default=0,null=False)
    user_id =  models.IntegerField(default=0,null=False)
    action =  models.CharField(max_length=100, null=False)
    trade_mode =  models.CharField(max_length=100, null=False)
    market_pair =  models.CharField(max_length=100, null=False)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    broker_unique_id = models.CharField(max_length=100, null=False,unique=False)
    coin_fee = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    temp_cost_amount  = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    temp_fee_amount = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    temp_cost_amount_after_fee  = models.DecimalField(null=True, max_digits=29, decimal_places=19)

    market_total_amount_submitted = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    market_total_amount_filled = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    coin_amount_filled = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    usd_rate_vnd = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    final_btc_price = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    final_usd_price = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    final_vnd_price = models.DecimalField(null=True, max_digits=29, decimal_places=19)
    total_fee = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    cost_amount = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    cost_amount_after_fee = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    final_money_added = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)

    wallet_payload = models.TextField()
    wallet_status = models.IntegerField(default=0,null=True)
    wallet_response = models.TextField()
    wallet_request_count = models.IntegerField(default=0,null=True)

    fulfillment_broker_unique_id = models.CharField(max_length=100, null=True,unique=False)

    system_status = models.CharField(max_length=100, null=False,db_index=True)
    

    class Meta:
        db_table = "exchanger_transaction_step_market"



class ExchangerWithdrawRequest(models.Model):
    ID = models.AutoField(primary_key=True)
    coin_id =  models.CharField(max_length=100, null=False)
    to_coin_address =  models.CharField(max_length=255, null=False)
    tag =  models.CharField(max_length=100, null=True)
    unique_id = models.CharField(max_length=255, null=False,unique=True)
    
    amount  = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    status = models.CharField(max_length=255, null=True)
    broker_reference_id = models.CharField(max_length=255, null=True)
    txid =  models.CharField(max_length=255, null=True)

    network = models.CharField(max_length=255, null=True)
    
    wallet_status = models.IntegerField(default='0')
    wallet_request_count = models.IntegerField(default='0')
    
    

    class Meta:
        db_table = "exchanger_withdraw_request"


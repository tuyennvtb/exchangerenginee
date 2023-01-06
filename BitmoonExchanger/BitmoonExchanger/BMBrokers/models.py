from django.db import models

# Create your models here.
class BrokerAccount(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,unique=True)
    api_key = models.CharField(max_length=256, null=False)
    api_secret = models.CharField(max_length=256, null=False)
    account_name = models.CharField(max_length=256, null=False)
    status = models.IntegerField(default=0,null=True)
    
    class Meta:
        db_table = "broker_account"

class CoinMarketCapModel(models.Model):
    ID = models.AutoField(primary_key=True)
    coin_id = models.CharField(max_length=100, null=False,unique=True)
    currency_id = models.IntegerField(default=0,null=True,unique=False)
    name = models.CharField(max_length=100, null=False)
    symbol = models.CharField(max_length=100, null=False)
    cmc_rank = models.IntegerField(default=0,null=True)
    price_usd = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    volume_usd_24h = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    percent_change_1h = models.DecimalField(null=True, max_digits=10, decimal_places=2,default=0)
    percent_change_24h = models.DecimalField(null=True, max_digits=10, decimal_places=2,default=0)
    percent_change_7d = models.DecimalField(null=True, max_digits=10, decimal_places=2,default=0)
    market_cap = models.DecimalField(null=True, max_digits=39, decimal_places=9, default=0)
    cmc_date_added = models.DateTimeField(null=True, db_index=True)
    cmc_last_updated = models.DateTimeField(null=True, db_index=True)

    created_at = models.DateTimeField(null=True, db_index=True)
    updated_at = models.DateTimeField(null=True, db_index=True)

    class Meta:
        db_table = "coinmarketcap_coin_listing"

class CoinMarketCapPairModel(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    market_pair = models.CharField(max_length=100, null=False,db_index=True)
    base_currency = models.CharField(max_length=100, null=False,db_index=True)
    market_currency = models.CharField(max_length=100, null=False,db_index=True)
    market_currency_id = models.IntegerField(default=0,null=True,db_index=True)

    created_at = models.DateTimeField(null=True, db_index=True)
    updated_at = models.DateTimeField(null=True, db_index=True)

    class Meta:
        db_table = "coinmarketcap_pair_listing"
        unique_together = [
            ['broker_id', 'market_pair']
        ]


class BrokerMarketPairModel(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    market_pair = models.CharField(max_length=100, null=False,db_index=True)
    base_currency = models.CharField(max_length=100, null=False,db_index=True)
    market_currency = models.CharField(max_length=100, null=False,db_index=True)   

    last_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    bid_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    ask_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)

    status = models.IntegerField(default=0,null=True)

    created_at = models.DateTimeField(null=True, db_index=True)
    updated_at = models.DateTimeField(null=True, db_index=True)

    class Meta:
        db_table = "broker_market_pair"
        unique_together = [
            ['broker_id', 'market_pair']
        ]

class BrokerCoinMappingModel(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    coin_id = models.CharField(max_length=100, null=True,db_index=True)   
    coin_name = models.CharField(max_length=100, null=True,default='Unknown')
    coin_symbol = models.CharField(max_length=100, null=False,db_index=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    status = models.IntegerField(default=0,null=True)

    description = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "broker_coin_mapping"
        unique_together = [
            ['broker_id', 'coin_id']
        ]

class BrokerCoinPriceModel(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    coin_name = models.CharField(max_length=100, null=True,default='Unknown')
    coin_symbol = models.CharField(max_length=100, null=False,db_index=True)
    base_currency = models.CharField(max_length=100, null=True)
    coin_id = models.CharField(max_length=100, null=True,db_index=True)

    usd_last_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0) 
    usd_bid_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    usd_ask_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)

    btc_last_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0) 
    btc_bid_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    btc_ask_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)

    


    created_at = models.DateTimeField(null=True, db_index=True)
    updated_at = models.DateTimeField(null=True, db_index=True)

    status = models.IntegerField(default=0,null=True)

    class Meta:
        db_table = "broker_coin_price"
        unique_together = [
            ['broker_id', 'coin_symbol']
        ]

class Broker_Account_Order(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    market_pair = models.CharField(max_length=100, null=False)
    mode = models.CharField(max_length=100, null=False)
    action = models.CharField(max_length=100, null=False,db_index=True)
    orderId = models.CharField(max_length=100, null=False,db_index=True)
    price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0) 
    quantity = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0) 
    fill_quantity = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    avg_price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    total_amount = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    status = models.CharField(max_length=100, null=False,default='NEW')

    class Meta:
        db_table = "broker_account_order"
        unique_together = [
            ['broker_id', 'orderId']
        ]

class Broker_Account_Balance(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    coin_symbol = models.CharField(max_length=100, null=False)
    free_balance = models.DecimalField(null=True,max_digits=29,decimal_places=8,default=0)
    locked_balance = models.DecimalField(null=True,max_digits=29,decimal_places=8,default=0)
    total_balance = models.DecimalField(null=True,max_digits=29,decimal_places=8,default=0)
    total_balance_in_usd = models.DecimalField(null=True,max_digits=29,decimal_places=8,default=0)
    updated_at = models.DateTimeField(null=True, db_index=True)

    class Meta:
        db_table = "broker_account_balance"
        unique_together = [
            ['broker_id', 'coin_symbol']
        ]


class Broker_Account_Deposit_History(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    account_id = models.CharField(max_length=100, null=True,db_index=True)
    coin_symbol = models.CharField(max_length=100, null=False)
    broker_history_id = models.CharField(max_length=255, null=False)
    amount = models.DecimalField(null=True,max_digits=29,decimal_places=8,default=0)
    confirmations = models.IntegerField(default='0')
    txid = models.CharField(max_length=255, null=False)
    crypto_address = models.CharField(max_length=255, null=False)
    crypto_address_tag = models.CharField(max_length=255, null=True)
    updated_at = models.DateTimeField(null=True, db_index=True)

    class Meta:
        db_table = "broker_account_deposit_history"
        unique_together = [
            ['broker_id', 'broker_history_id']
        ]

class Broker_Account_Deposit_Address(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    coin_symbol = models.CharField(max_length=100, null=False)   
    crypto_address = models.CharField(max_length=255, null=False)
    crypto_address_tag = models.CharField(max_length=255, null=True)
    chain =  models.CharField(max_length=255, null=True)
    account_id  = models.IntegerField(default=0,null=True)

    class Meta:
        db_table = "broker_account_deposit_address"
        unique_together = [
            ['broker_id', 'coin_symbol','chain','account_id']
        ]

class Broker_Coin_Info(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    coin_symbol = models.CharField(max_length=100, null=False)   
    withdraw_fee_type = models.CharField(max_length=255, null=False)
    min_transact_fee_withdraw = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    max_transact_fee_withdraw =  models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)
    status = models.CharField(max_length=255, null=True)
    deposit_status = models.IntegerField(null=True)
    withdraw_status = models.IntegerField(null=True)
    min_withdraw_amount = models.DecimalField(null=True, max_digits=29, decimal_places=9,default=0)
    
    class Meta:
        db_table = "broker_coin_info"
        unique_together = [
            ['broker_id', 'coin_symbol']
        ]


class Broker_Network_Info(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    coin_symbol = models.CharField(max_length=100, null=False)   
    network = models.CharField(max_length=100, null=False)
    network_name = models.CharField(max_length=255, null=False)
    is_default = models.BooleanField()
    withdraw_enable = models.BooleanField()
    deposit_enable =  models.BooleanField()
    address_regex = models.CharField(max_length=100, null=False)
    
    
    class Meta:
        db_table = "broker_network_info"
        unique_together = [
            ['broker_id', 'coin_symbol', 'network']
        ]


class Broker_Account_Order_Fill(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    market_pair = models.CharField(max_length=100, null=False)
    action = models.CharField(max_length=100, null=False,default='')
    orderId = models.CharField(max_length=100, null=False,db_index=True)
    trade_id = models.CharField(max_length=100, null=False,db_index=True)
    price = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0) 
    quantity = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)

    class Meta:
        db_table = "broker_account_order_fill"
        unique_together = [
            ['broker_id', 'trade_id']
        ]


class Broker_Withdraw_History(models.Model):
    ID = models.AutoField(primary_key=True)
    broker_id = models.CharField(max_length=100, null=False,db_index=True)
    coin_symbol = models.CharField(max_length=100, null=False)
    address = models.CharField(max_length=255, null=False,default='')
    unique_id = models.CharField(max_length=255, null=False,default='')
    txId = models.CharField(max_length=255, null=False,db_index=True)
    network = models.CharField(max_length=10, null=False,db_index=True)
    amount = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0) 
    fee = models.DecimalField(null=True, max_digits=29, decimal_places=19,default=0)

    class Meta:
        db_table = "broker_account_withdraw_history"
        unique_together = [
            ['broker_id', 'unique_id']
        ]

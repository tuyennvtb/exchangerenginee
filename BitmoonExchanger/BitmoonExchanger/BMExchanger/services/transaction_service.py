from ..business.transaction_business import TransactionBusiness
from ..business.trade_transaction_business import TradeTransactionBusiness
class TransactionService:
    def process_transaction(self,unique_id):
        TransactionBusiness(unique_id=unique_id).process()

    def process_trade_transaction(self,buy_unique_id,sell_unique_id):
        TradeTransactionBusiness(buy_unique_id=buy_unique_id,sell_unique_id=sell_unique_id).process()
    
    def match_broker_order(self,unique_id):
        TransactionBusiness(unique_id=unique_id).match_broker_order()

    def call_to_update_wallet(self, unique_id):
        TransactionBusiness(unique_id=unique_id).call_to_update_wallet()

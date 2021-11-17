import numpy as np
from datetime import timedelta

class OrderBrushing_fast:
    def __init__(self,array):
        self.array = array
        self.result = None
        self.output = None

    #########
    #metrics#
    #########
    #concentrate rate
    def concentrate_rate(self, array):
        total_orders = array[:,1].size
        total_unique_users = np.unique(array[:,2]).size
        return total_orders/total_unique_users

    #order proportion
    def order_proportion(self, array):
        user_orders = np.unique(array[:,2],return_counts=True)
        total_orders = array.shape[0]
        order_proportion = np.vstack([user_orders[0], user_orders[1]/total_orders])
        return order_proportion

    ####################
    #data preprocessing#
    ####################
    #add fraud time to array
    def add_1hr_time(self, array):
        new_col = (array[:,3] + timedelta(hours=1)).reshape(-1,1)
        self.array = np.hstack([array,new_col])
        return self.array

    #return all shop id
    def get_shop_id(self, array):
        shop_id = np.unique(array[:,1]).reshape(-1,1)
        return shop_id

    #get orders belonging to a specific shop
    def get_shop_array(self, array, shop_id):
        shop_array = array[array[:,1] == shop_id]
        return shop_array

    ##############
    #calculations#
    ##############
    #determine if user is suspicious, given a specific shop's order brushing orders
    #assumption: we assume the array contains order brushing orders
    def suspicious_users(self, array):
        users, user_proportion = self.order_proportion(array)
        highest_proportion = np.max(user_proportion)
        highest_proportion_user = users[user_proportion == highest_proportion]
        return highest_proportion_user

    #determine if a shop is order brushing
    def order_brushing_shop(self, array):
        concentrate_rate = self.concentrate_rate(array)
        return True if concentrate_rate>=3 else False

    ###########
    #algorithm#
    ###########
    #return an array that contains all the orders within 1hr period, given a specific row
    def get_investigation_array(self, array, row):
        start_time, end_time = array[row,3], array[row,4]
        orders_index = (array[:,3] >= start_time) & (array[:,3] <= end_time)
        investigation_array = array[orders_index]
        return investigation_array

    #investigate if there is order brushing behaviour for a given shop
    def investigate(self, array, shop_id):
        shop_array = self.get_shop_array(array, shop_id)
        shop_fraud_df = []
        orders_index = np.arange(shop_array[:,1].size)
        investigation_arrays = np.array(list(map(lambda x: self.get_investigation_array(shop_array,x),
                                                 orders_index)))
        frauds_index = np.array(list(map(self.order_brushing_shop, investigation_arrays)))
        if frauds_index.any():
            shop_fraud_array = np.vstack(investigation_arrays[frauds_index])
            fraud_users = self.suspicious_users(shop_fraud_array)
        else:
            fraud_users = 0
        return [shop_id, fraud_users]

    ############
    #production#
    ############
    #return our final result
    def get_output(self):
        return self.output

    #now let's run the magic
    def run(self):
        self.array = self.add_1hr_time(self.array)
        shop_ids = np.hstack(self.get_shop_id(self.array))
        self.result = np.array(list(map(lambda x: self.investigate(self.array, x), shop_ids)))
        self.output = pd.DataFrame([map(lambda df: df[0], self.result), map(lambda df: df[1], self.result)]).T
        self.output.columns = ['shopid','userid']
        self.output['userid'] = self.output['userid'].astype('str').str.replace(' ','&').\
                                    astype('str').str.replace('[','').str.replace(']','')
        return self

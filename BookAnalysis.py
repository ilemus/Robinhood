
class BookAnalyzer:
    def __init__(self):
        self.history = []
        self.time_ratio = []
    
    
    def load_data(self, filename):
        self.history = []
        self.time_ratio = []
        with open(filename, 'r') as f:
            for line in f:
                if line == '':
                    break
                line = line.replace('\n', '')
                arr = line.split(' ')
                bids = []
                asks = []
                count = 0
                for i in range(1, len(arr)):
                    pair = arr[i][1:len(arr[i]) - 1]
                    pair = pair.split(',')
                    if count < 10:
                        bids.append((float(pair[0]), int(pair[1])))
                        count += 1
                    else:
                        asks.append((float(pair[0]), int(pair[1])))
                # Dependent on decision to print bids in order, or from price to 10 ticks out
                bids.reverse()
                self.history.append((arr[0], bids, asks))
                # [0] is time, [1] to [10] are (bid price, bid size), [11] to [21] are (ask price, ask size)
            f.close()
        
    def set_ratio(self):
        for row in self.history:
            bid_orders = 0
            ask_orders = 0
            for bid in row[1]:
                bid_orders += bid[1]
            for ask in row[2]:
                ask_orders += ask[1]
            self.time_ratio.append((row[0], bid_orders, ask_orders))
            if ask_orders == 0:
                print(row[0] + "ASK ORDERS 0")
                return
            print(str(bid_orders) + "\t" + str(-1 * ask_orders))
            
    def assume_ratio_changes(self):
        prev_bid = self.history[0][1][0]
        prev_ask = self.history[0][2][0]
        output = [[0,0],[0,0]]
        for i in range(1, len(self.history)):
            if self.history[i][1][0] != prev_bid:
                is_up = prev_bid < self.history[i][1][0]
                
                prev_bid = self.history[i][1][0]
                prev_ask = self.history[i][2][0]
                # print(self.history[i][0] + " " + str(is_up))
                
                ratio_increase = self.time_ratio[i - 1][1] / float(self.time_ratio[i - 1][2]) < self.time_ratio[i][1] / float(self.time_ratio[i][2])
                a = 0 if is_up else 1
                b = 0 if ratio_increase else 1
                output[a][b] += 1
                # print(self.history[i][0] + "\t" + str(is_up) + "\t" + str(self.time_ratio[i - 1][1] / float(self.time_ratio[i - 1][2])) + "\t->\t" + str(self.time_ratio[i][1] / float(self.time_ratio[i][2])))
                
            elif self.history[i][2][0] != prev_ask:
                is_up = prev_ask < self.history[i][2][0]
                prev_bid = self.history[i][1][0]
                prev_ask = self.history[i][2][0]
                # print(self.history[i][0] + " " + str(is_up))
                
                ratio_increase = self.time_ratio[i - 1][1] / float(self.time_ratio[i - 1][2]) < self.time_ratio[i][1] / float(self.time_ratio[i][2])
                a = 0 if is_up else 1
                b = 0 if ratio_increase else 1
                output[a][b] += 1
                # print(self.history[i][0] + "\t" + str(is_up) + "\t" + str(self.time_ratio[i - 1][1] / float(self.time_ratio[i - 1][2])) + "\t->\t" + str(self.time_ratio[i][1] / float(self.time_ratio[i][2])))
                
            else:
                # print(self.history[i][0] + " ")
                pass
        # print(output)

    def print_spread(self):
        for row in self.history:
            print(str(row[1][0][0]) + "\t" + str(row[2][0][0]))
        
if __name__ == "__main__":
    ba = BookAnalyzer()
    ba.load_data("uber.book")
    ba.set_ratio()
    # ba.assume_ratio_changes()
    
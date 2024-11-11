class ItemSet:
    """
    Lớp lưu trữ thông tin của một itemSet bao gồm các item, TWU, Pro, và utility.
    """
    def __init__(self, items, twu=0, pro=0, utility=0):
        self.items = sorted(items)      # Danh sách các item
        self.TWU = twu                  # Transaction-Weighted Utility (TWU)
        self.Pro = pro                  # Xác suất (Probability)
        self.utility = utility          # Tiện ích (utility)
    
    def InItems(self, items):
        """
        Kiểm tra xem tất cả các phần tử trong itemset có nằm trong danh sách items đã cho không.
        """
        for item in self.items:
            if item not in items:
                return False
        return True

    def __repr__(self):
        return f"ItemSet(items={self.items}, TWU={self.TWU}, Pro={self.Pro}, Utility={self.utility})"
    
    def __eq__(self, other):
        if isinstance(other, ItemSet):
            return self.items == other.items
        return False
    
    def __hash__(self):
        return hash(tuple(self.items))


class PHUIUP:
    """
    Lớp chính chạy thuật toán
    """
    def __init__(self):
        self.start_timestamp = 0
        self.end_timestamp = 0
        self.memory_usage = 0
        self.TU = 0
        self.database_size = 0
        self.min_util = float()
        self.min_pro = float()
        self.list_HTWPUI = []
        self.list_PHUI = []

    # Bước 1: quét database để tính TWU và Pro của 1-itemsets
    def ReadDatabase(self, file_path):
        transactions = [] # List transactions của database
        dict_item = {}  # Dict lưu TWU và Pro cho từng 1-item

        with open(file_path, 'r') as file:
            for line in file:
                # Bỏ qua các dòng trống
                line = line.strip()
                if not line:
                    continue
                
                # Cấu trúc file input <Items>:<total_utility>:< :<probability>    
                parts = line.split(':')
                items = parts[0].split()
                total_utility = int(parts[1])
                item_utilities = list(map(int, parts[2].split()))
                probability = float(parts[3])

                # Tính tổng tiện ích TU của cơ sở dữ liệu
                self.TU += total_utility

                # Tính TWU và Pro cho từng item
                for item in items:
                    if item not in dict_item:
                        dict_item[item] = {'TWU': 0, 'Pro': 0}
                    dict_item[item]['TWU'] += total_utility
                    dict_item[item]['Pro'] += probability

                # Thêm giao dịch vào danh sách lưu trữ database
                transaction = {
                    'items': items,
                    'total_utility': total_utility,
                    'item_utilities': item_utilities,
                    'probability': probability
                }
                transactions.append(transaction)

        # Tạo các 1-ItemSet từ item_info
        one_item_sets = [ItemSet(items=[item], twu=info['TWU'], pro=info['Pro']) for item, info in dict_item.items()]
        
        # Cập nhật kích cỡ databse  
        self.database_size = len(transactions)

        # for transaction in transactions:
        #     print(transaction)
        # for itemSet in one_item_sets:
        #     print(itemSet)
        # print(self.database_size)
        # print(self.TU)
        return transactions, one_item_sets
        
    def Check_HTWPUI(self, list_ItemSet):

        result = []
        for itemSet in list_ItemSet:
            if itemSet.TWU >= self.TU * self.min_util and itemSet.Pro >= self.database_size * self.min_pro:
                result.append(itemSet)
        return result

    def Apriori_gen(self, prev_itemsets, k):
        """
        Sinh các ứng viên itemset cấp độ k từ các itemset trước đó (k-1) (prev_itemsets).
        """
        candidates = set()
    
        for i in prev_itemsets:
            for j in prev_itemsets:
                if i != j:
                    # Lấy union của hai ItemSet
                    union_items =  set(i.items).union(set(j.items))

                    # Chỉ lấy các union có k item
                    if len(union_items) == k:
                        candidates.add(ItemSet(union_items))
        return candidates

    def Calculate_TWU_Pro(self, itemsets, database):
        """
        Quét database để tính toán TWU(X) và Pro(X) cho các itemset X
        """

        for transaction in database:
            items = transaction['items']
            total_utility = transaction['total_utility']
            probability = transaction['probability']
            
            for itemset in itemsets:
                # Kiểm tra nếu itemset là tập con của giao dịch
                if set(itemset.items).issubset(set(items)):
                    itemset.TWU += total_utility
                    itemset.Pro += probability

        return itemsets

    # def Calculate_Utility_1transaction(self, itemset, transaction):
    #     """
    #     Tính tiện ích của một itemset trong một giao dịch cụ thể.
    #     """
    #     utility = 0
    #     for item in itemset.items:
    #         if item in transaction['items']:
    #             # Lấy chỉ số của item trong danh sách items để lấy utility
    #             i = transaction['items'].index(item)
    #             utility += transaction['item_utilities'][i]
    #     return utility

    # def Calculate_Utility(self, database):
    #     """
    #     Tính tiện ích thực tế của các itemset trong HTWPUIs.
    #     """
    #     for itemset in self.list_HTWPUI:
    #         total_utility = 0
    #         for transaction in database:
    #             if set(itemset.items).issubset(set(transaction['items'])):
    #                 total_utility += self.Calculate_Utility_1transaction(itemset, transaction)
            
    #         itemset.utility = total_utility
    #         # Kiểm tra có đúng HUI hay không
    #         if itemset.utility >= self.TU*self.min_util:
    #             self.list_PHUI.append(itemset)

    def Calculate_Utility(self, database):
        """
        Tính tiện ích thực tế của các itemset trong HTWPUIs bằng cách quét database một lần.
        """
        for transaction in database:
            items = transaction['items']
            item_utilities = transaction['item_utilities']

            for itemset in self.list_HTWPUI:
                if itemset.InItems(items):
                    # Tính tiện ích của itemset trong giao dịch hiện tại
                    utility = 0
                    for item in itemset.items:
                        if item in items:
                            index = items.index(item)
                            utility += item_utilities[index]
                    itemset.utility += utility

        # Kiểm tra HTWPUI có phải HUI
        for itemset in self.list_HTWPUI:
            if itemset.utility >= self.TU * self.min_util:
                self.list_PHUI.append(itemset)

    def run_algorithm(self, file_path, minUtil, minPro):
        self.start_timestamp = 0
        self.end_timestamp = 0
        self.memory_usage = 0
        self.TU = 0
        self.database_size = 0
        self.min_util = minUtil
        self.min_pro = minPro
        self.list_HTWPUI = []
        self.list_PHUI = []

        # Bước 1: Xử lý 1-itemsets (k = 1)
        database, one_item_sets = self.ReadDatabase(file_path)
        self.list_HTWPUI = self.Check_HTWPUI(one_item_sets)

        # Bước 2: Xử lý k-itemsets (k >= 2)
        prev_itemsets = self.list_HTWPUI.copy()
        k = 2
        while len(prev_itemsets) > 0:
            C_k = self.Apriori_gen(prev_itemsets, k)
            # print(f"k={k}: C_k: {C_k}\n")
            C_k = self.Calculate_TWU_Pro(C_k,database)
            prev_itemsets = self.Check_HTWPUI(C_k)
            for itemSet in prev_itemsets:
                self.list_HTWPUI.append(itemSet)
            k = k + 1

        self.Calculate_Utility(database)

        for itemSet in self.list_PHUI:
            print(itemSet)

           
#test
file_input = ".\data\input.txt"
minUtil = 0.25
minPro = 0.15
algorithm_PHUIUP = PHUIUP()
algorithm_PHUIUP.run_algorithm(file_input,minUtil, minPro)     


        



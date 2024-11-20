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
        Kiểm tra xem tất cả các phần tử trong itemset có nằm trong danh sách items không.
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
    def __init__(self):
        self.TU = 0
        self.database_size = 0
        self.min_util = float()
        self.min_pro = float()
        self.list_HTWPUI = []
        self.list_PHUI = []

    def ReadDatabase(self, file_path):
        """
        Quét database để tính TWU và Pro của 1-itemsets
        """

        transactions = [] # List transactions của database
        dict_item = {}  # Dict lưu TWU và Pro cho từng 1-item

        with open(file_path, 'r') as file:
            for line in file:
                # Bỏ qua các dòng trống
                line = line.strip()
                if not line:
                    continue
                
                # Cấu trúc file input <Items>:<total_utility>:<item_utilities>:<probability>    
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

        # Tạo các 1-ItemSet từ dict_item
        one_item_sets = [ItemSet(items=[item], twu=info['TWU'], pro=info['Pro']) for item, info in dict_item.items()]
        
        # Cập nhật kích cỡ databse  
        self.database_size = len(transactions)

        return transactions, one_item_sets
        
    def Check_HTWPUI(self, list_ItemSet):

        result = []
        for itemSet in list_ItemSet:
            if itemSet.TWU >= self.TU * self.min_util and itemSet.Pro >= self.database_size * self.min_pro:
                result.append(itemSet)
        return result

    def Apriori_gen(self, prev_itemsets, k):
            """
            Sinh các ứng viên itemset cấp độ k với cắt tỉa.
            """
            candidates = set()

            for i in prev_itemsets:
                for j in prev_itemsets:
                    if i != j:
                        # Lấy union của hai ItemSet
                        union_items = set(i.items).union(set(j.items))
                        # Chỉ lấy các union có k item
                        if len(union_items) == k:
                            new_itemset = ItemSet(union_items)

                            # Kiểm tra tất cả tập con (k-1) của new_itemset có trong prev_itemsets
                            flag = True
                            list_subset = self.generate_subsets(new_itemset.items, k - 1)
                            for subset in list_subset:
                                found = False
                                for itemset in prev_itemsets:
                                    if subset == itemset.items:
                                        found = True
                                        break
                                if found == False:
                                    flag = False
                                    break
                            
                            if flag == True:
                                candidates.add(new_itemset)
            
            return candidates


    def generate_subsets(self, itemset, size):
        """
        Tạo tất cả các tập con (k-1) từ itemset.
        """
        list_subset = []
        n = len(itemset)
        
        for i in range(n):
            subset = []
            for j in range(n):
                if i != j:
                    subset.append(itemset[j])
            
            if len(subset) == size:
                list_subset.append(subset)
        
        return list_subset

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
        print("list HTWPUI")
        for itemset in self.list_HTWPUI:
            print(itemset)
        print("\n\n")
            

    def run_algorithm(self, file_path, minUtil, minPro):
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

        # for itemSet in self.list_PHUI:
        #     print(itemSet)

class ITPHUI_PHUIUP_plus:
    """
    Lớp chính chạy thuật toán để tìm kiếm tương tác top k PHUI.
    """
    def __init__(self):
        self.start_timestamp = 0
        self.end_timestamp = 0
        self.memory_usage = 0
        self.list_TPHUI = []
        self.minUtil = minUtil
        self.list_k = list_k

    def run_algorithm(self, file_path, minUtil, list_k):
        self.start_timestamp = 0
        self.end_timestamp = 0
        self.memory_usage = 0
        self.list_TPHUI = []
        self.TU = 0
        self.minUtil = minUtil
        self.list_k = list_k

        # Chạy thuật toán PHUIUP để tìm tất cả PHUI có Pro >=0
        algorithm_PHUIUP = PHUIUP()
        algorithm_PHUIUP.run_algorithm(file_path, minUtil, 0)
        list_phui =  algorithm_PHUIUP.list_PHUI
        self.TU = algorithm_PHUIUP.TU
        
        # Sắp xếp danh sách PHUI tìm được theo chiều giảm dần của Pro
        list_phui.sort(key=lambda x: x.Pro, reverse=True)

        # Tiến hành tìm kiếm tương tác top-k
        for k in list_k:
            if k > 0 and k <= len(list_phui):
                top_k_phui = list_phui[:k]
                self.list_TPHUI.append(top_k_phui)
            elif k > 0 and k > len(list_phui):
                top_k_phui = list_phui
                self.list_TPHUI.append(top_k_phui)
            else:
                self.list_TPHUI.append([])
            
    def print_result(self):
        print(f"minutil = {self.minUtil}% of {self.TU} ({self.minUtil*self.TU})")
        k = 0
        for i in self.list_TPHUI:
            print(f"k = {self.list_k[k]}")
            k += 1
            for j in i:
                print(j)
            print()
            print("----------------------------------")

if __name__ == '__main__':
    # Test
    # file_path = "./input/input_abc.txt"
    file_path = "./input/retail_utility_probability.txt"
    minUtil = 0.01
    list_k = [1, 3, 5, 7, 10, 20]

    algorithm = ITPHUI_PHUIUP_plus()
    algorithm.run_algorithm(file_path, minUtil, list_k)
    algorithm.print_result()
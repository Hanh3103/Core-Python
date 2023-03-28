from datetime import datetime
import json
import re


class Bus:
    def __init__(self, bus_id):
        self.bus_id = bus_id
        self.bus_stops_dict = {}  # {1:name, 2:name}
        self.bus_stop_type = {"S": [], "O": [], "F": [], "X": []}  # {S:[stop_id], O:[], F:[]}
        self.stop_arrival_time = {}  # {1: (a_time, next_stop), }

    def add_stop(self, stop_id, stop_name):
        if stop_id not in self.bus_stops_dict.keys():
            self.bus_stops_dict[stop_id] = stop_name

    def add_stops_to_bus(self, stop_type, stop_id):
        if stop_type in ["S", "O", "F"] and stop_id not in self.bus_stop_type[stop_type]:
            self.bus_stop_type[stop_type].append(stop_id)
        if stop_type == "" and stop_id not in self.bus_stop_type["X"]:
            self.bus_stop_type["X"].append(stop_id)

    def add_arrival_time_next_stop(self, stop_id, stop_arr_t, next_st):
        if stop_id not in self.stop_arrival_time.keys():
            self.stop_arrival_time[stop_id] = (stop_arr_t, next_st)

    def get_all_stops(self):
        temp = list(
            set(self.bus_stop_type["S"]).union(set(self.bus_stop_type["O"])).union(set(self.bus_stop_type['F'])).union(set(self.bus_stop_type['X'])))
        return [self.bus_stops_dict.get(i) for i in temp]

    def __str__(self):
        # bus_stops_str = ", ".join([f"{k}: {v}" for k, v in self.bus_stops_dict.items()])
        # return f"{bus_stops_str}"
        # b_S = ", ".join([f"{k}: {self.bus_stops_dict.get(k)}" for k in self.bus_stop_type['S']])
        b_s = ", ".join([f"{self.bus_stops_dict.get(k)}" for k in self.bus_stop_type['S']])
        b_o = ", ".join([f"{self.bus_stops_dict.get(k)}" for k in self.bus_stop_type['O']])
        b_f = ", ".join([f"{self.bus_stops_dict.get(k)}" for k in self.bus_stop_type['F']])
        s = len(self.bus_stop_type['S'])
        o = len(self.bus_stop_type['O'])
        f = len(self.bus_stop_type['F'])
        # return f"Bus {self.bus_id}: Stops - S:{b_S}, O:{b_O}, F:{b_F}"
        return f"Start stops: {s} [{b_s}] \n Transfer stops:{o} [{b_o}] \n Finish stops:{f} [{b_f}]"


class EasyRider:
    def __init__(self, json_string):
        self.json_data_object = json.loads(json_string)
        self.required_fields = ["bus_id", "stop_name", "next_stop", "a_time"]
        self.regex_name = r'^[A-Z][a-z]+(?: [A-Z][a-z]*)* (Street|Road|Avenue|Boulevard)$'  # ["Street", "Road",
        # "Avenue", "Boulevard"]
        self.regex_time = r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$"
        self.bus_id_list = {}
        self.bus_list = {}

        """^: Match the start of the string (?:[01][0-9]|2[0-3]): Match either 00 to 19, or 20 to 23 :: Match a colon 
        [0-5][0-9]: Match any number from 00 to 59 $: Match the end of the string This regular expression uses a 
        non-capturing group (?:xxxx) to match either hours 00 to 19, or 20 to 23. The [0-5][0-9] pattern matches any 
        number from 00 to 59 for the minutes. The ^ and $ anchors ensure that the entire string matches this pattern, 
        with no additional characters before or after the time. """

        """
        """

    def check_data_type(self):
        expected_data_type = {
            "bus_id": int,
            "stop_id": int,
            "stop_name": str,
            "next_stop": int,
            "stop_type": str,
            "a_time": str}
        total_errors = 0
        field_errors = {fd: 0 for fd in expected_data_type.keys()}

        for record in self.json_data_object:
            for fd in expected_data_type.keys():
                value = record[fd]
                if value is None:
                    field_errors[fd] += 1
                    total_errors += 1
                elif type(value) != expected_data_type[fd]:  # check data type
                    field_errors[fd] += 1
                    total_errors += 1
                elif fd == "stop_type":  # check stop_type when data type right
                    if len(value) >= 2 or (value not in ["S", "O", "F"] and value != ""):
                        field_errors[fd] += 1
                        total_errors += 1
                elif fd == "stop_name":
                    if not re.match(self.regex_name, value):
                        field_errors[fd] += 1
                        total_errors += 1
                elif fd == "a_time":
                    if not re.match(self.regex_time, value):
                        field_errors[fd] += 1
                        total_errors += 1

                if fd in self.required_fields:
                    if value is None or (expected_data_type[fd] == str and value == ""):
                        field_errors[fd] += 1
                        total_errors += 1

        print(f'Format validation: {total_errors} errors')
        for field in ["stop_name", "stop_type", "a_time"]:
            print(f'{field}: {field_errors[field]}')

    def find_n_stops(self):
        for record in self.json_data_object:
            bus_num = record['bus_id']
            bus_stop_id = record['stop_id']
            if bus_num not in self.bus_id_list.keys():
                self.bus_id_list[bus_num] = []
            if bus_stop_id not in self.bus_id_list[bus_num]:
                self.bus_id_list[bus_num].append(bus_stop_id)
        # print("Line names and number of stops:")
        # for key in self.bus_id_list.keys():
        # print(f'bus_id: {key}, stops: {len(self.bus_id_list[key])}')

    def find_all_stops_of_bus(self):
        self.get_bus_list()

        start_stops = []
        trans_stops_count = {}
        fin_stops = []
        o_d_stops = []
        tmp = False
        for bus_id, bus in self.bus_list.items():
            if len(bus.bus_stop_type['S']) == 0 or len(bus.bus_stop_type['F']) == 0:
                print(f'There is no start or end stop for the line: {bus_id}')
                # tmp = True
                return
            else:
                for k in bus.bus_stop_type['S']:
                    if bus.bus_stops_dict.get(k) not in start_stops:
                        start_stops.append(bus.bus_stops_dict.get(k))

                for k in bus.bus_stop_type['F']:
                    if bus.bus_stops_dict.get(k) not in fin_stops:
                        fin_stops.append(bus.bus_stops_dict.get(k))

                for k in bus.bus_stop_type['O']:
                    if bus.bus_stops_dict.get(k) not in o_d_stops:
                        o_d_stops.append(bus.bus_stops_dict.get(k))

                for stop in bus.get_all_stops():
                    if stop not in trans_stops_count.keys():
                        trans_stops_count[stop] = 1
                    else:
                        trans_stops_count[stop] += 1

        # if not tmp:
        transfer_stops = [stop for stop, count in trans_stops_count.items() if count > 1]
        start_stops.sort()
        fin_stops.sort()
        transfer_stops.sort()
        # print( f'Start stops: {len(start_stops)} {start_stops}\nTransfer stops: {len(transfer_stops)} {
        # transfer_stops}' f'\nFinish stops: {len(fin_stops)} {fin_stops}')
        return start_stops, fin_stops, transfer_stops, o_d_stops

    def get_bus_list(self):
        for record in self.json_data_object:
            bus_i = record['bus_id']
            stop_id = record['stop_id']
            stop_name = record['stop_name']
            stop_type = record['stop_type']
            stop_ar_time = record['a_time']
            next_st = record['next_stop']
            if bus_i not in self.bus_list.keys():
                bus = Bus(bus_i)
                bus.add_stops_to_bus(stop_type, stop_id)
                bus.add_stop(stop_id=stop_id, stop_name=stop_name)
                bus.add_arrival_time_next_stop(stop_id=stop_id, stop_arr_t=stop_ar_time, next_st=next_st)
                self.bus_list[bus_i] = bus
            else:
                self.bus_list[bus_i].add_stop(stop_id=stop_id, stop_name=stop_name)
                self.bus_list[bus_i].add_stops_to_bus(stop_type=stop_type, stop_id=stop_id)
                self.bus_list[bus_i].add_arrival_time_next_stop(stop_id=stop_id, stop_arr_t=stop_ar_time,
                                                                next_st=next_st)

    def convert_str_date(self, in_str):
        return datetime.strptime(in_str, '%H:%M')

    def check_arrival_time(self):
        print("Arrival time test:")
        for bus_id, bus in self.bus_list.items():
            for stop_id in bus.stop_arrival_time.keys():
                value = bus.stop_arrival_time[stop_id]
                # print(value)
                next_stop = value[1]
                # print(next_stop)
                if next_stop != 0:
                    ar_ti_ne = bus.stop_arrival_time[next_stop][0]
                    if not self.convert_str_date(value[0]) <= self.convert_str_date(ar_ti_ne):
                        print(f'bus_id line {bus_id}: wrong time on station {bus.bus_stops_dict.get(next_stop)}')
                        return

        print("OK")
        return

    def check_one_demand(self):
        print("On demand stops test:")
        error = []
        start, end, tran, od = self.find_all_stops_of_bus()
        print(start, end, tran, od)
        i_1 = set(start).intersection(set(od))
        i_2 = set(end).intersection(set(od))
        i_3 = set(tran).intersection(set(od))
        i_finale = list(set(i_1.union(i_2).union(i_3)))
        i_finale.sort()
        if len(i_finale) > 0:
            print(f'Wrong stop type: {i_finale}')
        else:
            print("OK")


if __name__ == '__main__':
    data = input()
    test = EasyRider(data)
    test.check_one_demand()

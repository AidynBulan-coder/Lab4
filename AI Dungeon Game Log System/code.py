from datetime import datetime
import json
import random
class Player:
    def __init__ (self,id,name,hp):
        self._id = id
        self._name = name.strip().title()
        self._hp = max(0,hp)
        self._max_hp = self._hp 
        self._inventory = Inventory()        
    @property
    def hp(self):
        return self._hp
    @hp.setter
    def hp(self,value):
        self._hp = max(0,value)
        self._hp = min(self._max_hp,self._hp)
    @property
    def inventory(self):
        return self._inventory
    @classmethod
    def from_string(cls,data):
        parts = data.split(",")
        if len(parts) != 3:
            raise ValueError("Введите ('Id,name,hp')")
        id,name,hp = parts
        try:
            id_val = int(id)
            hp_val = max(0,int(hp))
        except:
            raise ValueError("id и hp должны быть числами")
        name_val = name.strip().title()
        return cls(id_val,name_val,hp_val)
    def __str__(self):
        return f"Player(id = {self._id}, name = {self._name}, hp = {self._hp})"
    def __del__(self):
        print(f"Player {self._name} deleted")
    def handle_event(self,event):
        if not isinstance(event,Event):
            raise ValueError("Event error")
        else:
            if event._event_type == "ATTACK":
                self._hp -= event._data["damage"]
                self._hp = max(0,self._hp)
            elif event._event_type == "HEAL":
                self._hp = min(self._max_hp,self._hp + event._data["heal"])
            elif event._event_type == "LOOT":
                item = event._data["item"]
                self._inventory.add_item(item)
class Warrior(Player):
    def handle_event(self,event):
        if event._event_type == "ATTACK":
                event._data["damage"] = int(event._data["damage"] * 0.9)
        super().handle_event(event)
class Mage(Player):
    def handle_event(self,event):
        if event._event_type == "LOOT":
                item = event._data["item"]
                event._data["item"] = item.to_dict()
                event._data["item"] = Item(item._id, item._name, int(item._power * 1.1))
        super().handle_event(event)
class Item:
    def __init__(self,id,name,power):
        self._id = id
        self._name = name.strip().title()
        self._power = power
    @classmethod
    def from_string(cls,data):
        parts = data.split(",")
        if len(parts) != 3:
            raise ValueError("Введите ('Id,name,power')")
        id,name,power = parts
        try:
            id_val = int(id)
            power_val = int(power)
        except:
            raise ValueError("id и power должны быть числами")
        name_val = name.strip().title()
        return cls(id_val,name_val,power_val)
    def __str__(self):
        return f"Item(id = {self._id}, name = {self._name}, power = {self._power})"
    def __del__(self):
        print(f"Item {self._name} deleted")
    def __eq__(self, other):
        if isinstance(other,Item):
            return self._id == other._id
        return False
    def __hash__(self):
        return hash(self._id)   
    def to_dict(self):
        return{
            "id":self._id,
            "name":self._name,
            "power":self._power
        }
class Inventory:
    def __init__(self):
        self._items = []
    def add_item(self,item):
        if isinstance(item,Item):
            if item not in self._items:
                self._items.append(item)
    def remove_item(self,item_id):
        self._items = [item for item in self._items if item._id != item_id]
    def get_items(self):
        return self._items
    def unique_items(self):
        return set(self._items)
    def to_dict(self):
        return {item._id: item for item in self._items}
    def get_strong_items(self,min_power):
        return list(filter(lambda item:item._power >= min_power,self._items))
    def __iter__(self):
        inventory = self._items
        return iter(inventory)
class Event:
    def __init__(self,event_type,data,player_id):
        self._player_id = player_id
        self._event_type = event_type
        self._data = data
        self._timestamp = datetime.now()
        event_types = ["ATTACK","HEAL","LOOT"]
        if self._event_type not in event_types:
            raise ValueError("Wrong event type.Choose 'ATTACK','HEAL','LOOT'")
    def __str__(self):
        return f"Event(type = '{self._event_type}', data={self._data}, timestamp = '{self._timestamp}')"
class Logger:
    @staticmethod
    def log(event,player,filename):
        if not isinstance(player,Player):
            raise ValueError("player have to be object Player")
        if not isinstance(event,Event):
            raise ValueError("event have to be object Event")
        log_line = f"{event._timestamp};{player._id};{event._event_type};{json.dumps(event._data,default = lambda o:o.to_dict())}\n"
        with open(filename,"a",encoding="utf-8") as f:
            f.write(log_line)
    @staticmethod
    def read_logs(filename):
        with open(filename,"r",encoding="utf-8") as f:
            events = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                timestamp_str , player_id,event_type,data_str = line.split(";",3)
                data = json.loads(data_str)
                event = Event(event_type,data,int(player_id))
                event._timestamp = timestamp_str
                events.append(event)
        return events
class EventIterator:
    def __init__(self, events):
        self._events = events 
        self._index = 0        

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._events):
            event = self._events[self._index]
            self._index += 1
            return event
        else:
            raise StopIteration
def damage_stream(events):
    for event in events:
        if event._event_type == "ATTACK":
            yield event._data["damage"]
def generate_events(players,items,n):
    events = []
    event_types = ["ATTACK","HEAL","LOOT"]
    for player in players:
        for _ in range(n):
            event_type = (lambda: random.choice(event_types))()
            if event_type == "ATTACK":
                data = {"damage":random.randint(10,20)}
            elif event_type == "HEAL":
                data = {"heal":random.randint(10,20)}
            elif event_type == "LOOT":
                data = {"item":random.choice(items)}
            event = Event(event_type,data,player._id)
            events.append(event)
    return events
def analyze_logs(events):
    total_damage = 0
    top_player_damage = {}
    most_common_event = {}
    result = {}
    for event in events:
        if event._event_type == "ATTACK":
            total_damage += event._data["damage"]
            player = event._player_id
            damage = event._data["damage"]
            if player in top_player_damage:
                top_player_damage[player] += damage
            else:
                top_player_damage[player] = damage
        if event._event_type in most_common_event:
            most_common_event[event._event_type] += 1
        else:
            most_common_event[event._event_type] = 1
    most_common = max(most_common_event,key=most_common_event.get)
    if top_player_damage:
        top_player = max(top_player_damage, key=top_player_damage.get)
    else:
        top_player = None
    result = {
        "total_damage": total_damage,
        "most_common_event": most_common,
        "top_player":top_player
    }
    return result
def decide_action(player,items):
    hp = player._hp
    inventory = player._inventory
    events = []
    if hp < 50:
        event_type = "HEAL"
        data = {"heal":random.randint(30,50)}
        player_id = player._id
        event = Event(event_type,data,player_id)
        events.append(event)
    elif len(inventory.get_items()) <= 3:
        event_type = "LOOT"
        data = {"item":random.choice(items)}
        player_id = player._id
        event = Event(event_type,data,player_id)
        events.append(event)
    else:
        event_type = "ATTACK"
        player_id = player._id
        data = {"damage":random.randint(20,30)}
        event = Event(event_type,data,player_id)
        events.append(event)
    return events
def analyze_inventory(player):
    result = {}
    items = set(player._inventory.get_items())
    top_power = max(items,key = lambda item:item._power)
    result = {
        "unique_items" :items,
        "top_power":top_power
    }
    return result
def main():
    open("main.txt", "w", encoding="utf-8").close()
    players = [
        Warrior.from_string("1,Arthur Pendragon,100"),
        Mage.from_string("2,Rupert_Night,120")
    ]
    items = [
        Item.from_string("1,Excalibur,200"),
        Item.from_string("2,Sphere,90")
    ]
    events = [
        Event("LOOT",{"item":items[0]},1),
        Event("LOOT",{"item":items[1]},2),
        Event("ATTACK",{"damage":200},1),
        Event("ATTACK",{"damage":99},2),
        Event("HEAL",{"heal":100},1)
    ]
    for event in events:
        for player in players:
            if player._id == event._player_id:  
                Logger.log(event,player,"main.txt")  
                player.handle_event(event)
                

    loaded = Logger.read_logs("main.txt")
    result = analyze_logs(loaded)
    with open("main.txt","a",encoding="utf-8") as f:
        f.write("STATS")
        f.write(json.dumps(result,indent = 2))
    return result
if __name__ == "__main__":
    print(main())

# uvicorn api:app --reload
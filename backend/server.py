from backend.vertex import Vertex


class Server(Vertex):

    def __init__(self, graph, id, owner=None):
        self.__type = "empty"
        self.__owner = owner
        # все ли проверки присутствуют - есть только война
        self.__enabled = 1
        self.__k = 0.0
        self.__power = 100
        self.__next_price = 10000
        self.__id = id
        self.__x = 0
        self.__y = 0
        super().__init__(graph)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        

    def is_enabled(self):
        return self.__enabled

    def turn_on(self):
        self.__enabled = 1

    def turn_off(self):
        self.__enabled = 0

    def set_type(self, new_type, crypt=None):
        self.__type = new_type
        if new_type == "attack":
            self.__k = 0.5
        elif new_type in self.get_graph().get_curr():
            self.__k = 0.5
        elif new_type == "SSH":
            self.__k = 0.0
        elif new_type == "defence":
            self.__k = 1.0
        elif new_type == "empty":
            self.__k = 0.7
        elif new_type == "support":
            self.__k = 0.0

    def set_owner(self, new_owner):
        self.__owner = new_owner

    def get_owner(self):
        return self.__owner

    def set_power(self, new_power):
        self.__power = new_power

    def get_power(self):
        return self.__power
    
    def set_next_price(self, new_price):
        self.__next_price = new_price

    def get_next_price(self):
        return self.__next_price

    def get_type(self):
        return self.__type

    def get_id(self):
        return self.__id

    def get_k(self):
        return self.__k
    
    def get_x(self):
        return self.__x
    
    def set_x(self, x):
        self.__x = x

    def get_y(self):
        return self.__y
    
    def set_y(self, y):
        self.__y = y

    def get_level(self):
        """для ресурсов с SSH"""
        # TODO: rewrite formula
        return self.__power/100

    def get_moves(self):
        """показывает сколько ресурсов даёт SSH"""
        if self.__type != "SSH":
            return 0
        # TODO: rewrite formula
        return self.get_level()

    def get_crypto_money(self):
        """показывает сколько ресурсов даёт mining"""
        if not(self.__type in self.get_graph().get_curr()):
            return 0
        # TODO: rewrite formula
        return self.get_power()

    def get_support_neighbours(self):
        support_neighbours = []
        for s in self.get_neighbours():
            if s.get_type() == "support":
                support_neighbours.append(s)
        return support_neighbours

    def get_power_gift(self):
        if self.__type != "support":
            return 0
        try:
            return self.__power / (len(self.get_neighbours()) - len(self.get_support_neighbours()))
        except Exception as e:
            # все соседи - поддержка
            return 0

    def print(self, prefix=""):
        print(prefix + str(self))
        print(prefix + "    " + str(self.__id) + " (" + str(self.__x)+","+str(self.__y)+")")
        print(prefix + "    " + self.__type)
        print(prefix + "    " + (self.__owner.GetName() if self.__owner is not None else "None"))
        print(prefix + "    " + str(self.__power))
        print(prefix + "    " + str(self.get_power_gift()))
        try:
            print(prefix + "    " + str(self.get_support_neighbours()))
        except TypeError:
            pass
    def __str__(self):
        return str(self.__id)+"("+str(self.__owner)+"|"+self.__type+")"

class A(object):
    def __init__(self):
        self.a = "a"
        
    def get_b(self):
        return self.b
        

class B(object):
    def __init__(self):
        self.b = "b"
        
    def get_a(self):
        return self.a


class AB(A, B):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    ab = AB()
    print(ab.get_b())

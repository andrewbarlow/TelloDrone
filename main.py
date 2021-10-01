class PathTree:
    def __init__(self, data):
        self.data = data
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def get_level(self):
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent

        return level

    def print_tree(self):
        print(self.data)
        if self.children:
            for child in self.children:
                child.print_tree()


def buildTree():
    root = PathTree("Electronics")

    laptop = PathTree("Laptop")

    root.add_child(laptop)

    print(laptop.get_level())

    return root


if __name__ == '__main__':
    root = buildTree()
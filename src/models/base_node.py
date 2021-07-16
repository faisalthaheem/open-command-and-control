# based on https://gist.github.com/nbassler/342fc56c42df27239fa5276b79fca8e6


class BaseNode(object):

    def __init__(self, data):
        self._data = data
        if type(data) == tuple:
            self._data = list(data)
        if type(data) is str or not hasattr(data, '__getitem__'):
            self._data = [data]

        self._columncount = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0

    def data(self, column):
        if column >= 0 and column < len(self._data):
            return self._data[column]

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if row >= 0 and row < self.childCount():
            return self._children[row]

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def addChild(self, child):
        """First item of the tuple has to be the id"""
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)
        self._columncount = max(child.columnCount(), self._columncount)


    def hasChild(self, child_id):
        """Checks to see if child_id is contained in the _children member"""
        """Returns Child instance if child is found, None otherwise"""
        for c in self._children:
            if c._data[0] == child_id:
                return c

        return None

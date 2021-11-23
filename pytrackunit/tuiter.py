"""iterator for tucache data"""

class ReqIter:
    """iterator for web (url) requests"""
    def __init__(self,cache,requests,meta=None):
        self.cache = cache
        self.requests = requests
        self.iter_started = False
        self.meta = meta

    def __aiter__(self):
        if self.iter_started:
            raise Exception("cant start tuiter more than once")
        self.iter_started = True
        return self

    async def __anext__(self):
        try:
            return await self.cache.get_url(next(self.requests)) , self.meta
        except StopIteration as exc:
            raise StopAsyncIteration from exc

class SqlIter:
    """iterator for tucache data"""
    def __init__(self, sqliter, meta=None):
        self.sqliter = sqliter
        self.iter_started = False
        self.meta = meta

    def __aiter__(self):
        if self.iter_started:
            raise Exception("cant start tuiter more than once")
        self.iter_started = True
        return self

    async def __anext__(self):
        try:
            return next(self.sqliter) , self.meta
        except StopIteration as exc:
            raise StopAsyncIteration from exc

class TuIter:
    """iterator holding all internal iterators"""
    def __init__(self) -> None:
        self.iterators = []
        self.iterator_pos = 0
        self.iter_started = False

    def add(self,_iter):
        """addes an internal iterator to this iterators list"""
        self.iterators.append(_iter)

    def __aiter__(self):
        if self.iter_started:
            raise Exception("cant start tuiter more than once")
        self.iter_started = True
        return self

    async def __anext__(self):
        try:
            return await self.iterators[self.iterator_pos].__anext__()
        except StopAsyncIteration as exc:
            self.iterator_pos += 1
            if self.iterator_pos >= len(self.iterators):
                raise StopAsyncIteration from exc
            return await self.__anext__()

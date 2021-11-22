"""iterator for tucache data"""

class ReqIter:
    """iterator for web (url) requests"""
    def __init__(self,cache,requests,previter=None):
        self.cache = cache
        self.requests = requests
        self.previter = previter
        self.previter_finished = previter is None
        self.iter_started = False

    def __aiter__(self):
        if self.iter_started:
            raise Exception("cant start tuiter more than once")
        self.iter_started = True
        return self

    async def __anext__(self):
        if not self.previter_finished:
            try:
                return await next(self.previter)
            except StopAsyncIteration:
                self.previter_finished = True
        try:
            return await self.cache.get_url(next(self.requests))
        except StopIteration as exc:
            raise StopAsyncIteration from exc

class SqlIter:
    """iterator for tucache data"""
    def __init__(self, sqliter, previter = None):
        self.sqliter = sqliter
        self.previter = previter
        self.previter_finished = previter is None
        self.iter_started = False

    def __aiter__(self):
        if self.iter_started:
            raise Exception("cant start tuiter more than once")
        self.iter_started = True
        return self

    async def __anext__(self):
        if not self.previter_finished:
            try:
                return await next(self.previter)
            except StopAsyncIteration:
                self.previter_finished = True
        try:
            return next(self.sqliter)
        except StopIteration as exc:
            raise StopAsyncIteration from exc

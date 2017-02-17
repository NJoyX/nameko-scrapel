from nameko.rpc import rpc
from scrapel import Scrapel, Request, Response
from scrapel.middleware.spider import PROCESS_INPUT, PROCESS_OUTPUT, PROCESS_EXCEPTION
from scrapel.middleware.download import PROCESS_REQUEST, PROCESS_RESPONSE, PROCESS_EXCEPTION


class MyClass(object):
    name = 'ticketland.ru'

    scrapper = Scrapel(
        allowed_domains=['ticketland.ru']
    )

    @scrapper.start_requests
    def one(self, url):
        yield Request(url, callback=self.two, dont_filter=True)

    def two(self, response):
        pass

    @scrapper.middleware(PROCESS_INPUT, priority=10)
    def lala(self, response):
        pass

    @scrapper.pipeline
    def one_pipe(self, response, item):
        pass

    @scrapper.on_start
    def started(self, ...):
        pass

    @scrapper.on_stop
    def stopped(self, ...):
        pass

    @rpc
    def start(self, url, **kwargs):
        self.scrapper.settings.set(**kwargs)
        self.scrapper.start(url)
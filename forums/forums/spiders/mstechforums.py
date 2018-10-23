from scrapy import Spider, Request
from forums.items import ForumsItem
import re

# concurrent page-crawling
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

#class MstechforumsSpider(CrawlSpider): # Concurrent crawls
class MstechforumsSpider(Spider):       # Single crawl
    name = 'mstechforums'
    allowed_domains = ['social.technet.microsoft.com']
    #allowed_urls = ['https://social.technet.microsoft.com/']
    start_urls = ['https://social.technet.microsoft.com/Forums/en-us/home?sort=lastpostdesc&brandIgnore=true&page=1']
    print("{}\nStart URLs = {}".format('*'*50,start_urls))

    custoem_settings = { 'LOG_LEVEL': 'ERROR'}

    # concurrent crawls
    rules = [
        # test run with just crawling a few pages concurrently
    #    Rule(LinkExtractor(allow=('page=[2-10]$')), callback='parse_list', follow=True)
        Rule(LinkExtractor(allow=('page=\d$')), callback='parse_main', follow=True)
    ]

#    def parse_main(self, response):    # Concurrent crawls
    def parse(self, response):          # Single crawl

        self.log('\n\n{}\n\t\tSCRAPING STARTED\n{}\n'.format('-'*50,'-'*50))

        # >>> For future use
        Filter = re.sub('\s', '', \
            (re.sub(r'\r\n','',response.css('.selectedOption::text')[0].extract())))
        Sort = re.sub('\s', '', \
            (re.sub(r'\r\n','',response.css('.selectedOption::text')[1].extract())))
        print('Filter: {}   Sort: {}'.format(Filter,Sort))
        # <<<

        startThread, threadPerPage, totalThreads = \
            map(lambda x: int(x), re.findall('\d+',response.css('.itemSpan::text').extract_first()))
        
        totalPages = int(totalThreads)//int(threadPerPage) + 1

        print('Total Threads = {}\nThreads per Page = {}\nTotal Pages = {}'.format(totalThreads, threadPerPage, totalPages))
        #-------------------------------------------------------------------
        # After the coding is done, while testing at the boundary it turned out
        # the the site will display 10,000 threads or 500 pages at most. And on
        # page 500, it will still show the 'Next >' at the bottom and clickable.
        # Nevertheless, upon accessing page 501 and beyond, it results with the 
        # error: 'The search service is down. Please link directly to threads 
        # and come back later.' Essentially, the site will presnet 500 pages
        # and not further. Hence, here the last page is here hard-coded to 
        totalPages = 500
        print("Reset 'Total Pages' to {} which is the most pages the site allows.".format(totalPages))
        #-------------------------------------------------------------------
        
        target_urls = [
            'https://social.technet.microsoft.com/Forums/en-us/home?sort=lastpostdesc&brandIgnore=true&page={}'\
            .format(x) for x in range(1,totalPages+1)  
            ]

        print('Yielding...')

        for url in target_urls[:5]: # for test run
        # for url in target_urls:    # for production run

            yield Request(url=url, callback=self.parse_the_page(self,response))

            nextClick = response.css('#threadPager_Next::text').extract_first()
            if nextClick != 'Next ›': break  # No more page to scrap
        
        print('Yielded...')
        self.log('\n{}\n\t\tSCRAPING ENDED\n{}\n\n'.format('-'*50,'-'*50))
            
    def parse_the_page(self, response):

        # totalThreads is a holding place and not used.
        startThread, lastThread, totalThreads = \
            map(lambda x: int(x), re.findall('\d+',response.css('.itemSpan::text').extract_first()))
        
        for thread in response.css('li.threadblock'):

            forumsItem = ForumsItem()

            for i in range(startThread, lastThread+1):
                try:
                    forumsItem[i] = {
                        "votes": int((re.findall('\d+', thread.css('div.votes div::text')[0].extract()))[0]),
                        "threadState": thread.css('.metrics.smallgreytext > span.statefilter > a::text')[0].extract(),
                        "replyCount": int((re.findall('\d+', thread.css('.replycount::text')[0].extract()))[0]),
                        "viewCount": int((re.findall('\d+', thread.css('.viewcount::text')[0].extract()))[0]),

                        "threadTitle": thread.css('.detailscontainer > h3 >a::text')[0].extract(),
                        "threadTitleLink": thread.css('.detailscontainer > h3 >a::attr(href)').extract_first(),
                        "threadSummary": thread.css('.threadSummary::text')[0].extract(),

                        "createdByName": re.sub(r"\ \-\ $", '', thread.css('.lastpost > a > span::text')[0].extract()),
                        "createdByLink": thread.css('.lastpost a:nth-child(2)::attr(href)')[1].extract(),
                        "createdByTime": thread.css('.lastpost span:nth-child(3)::text')[0].extract(),

                        "lastReplyName": re.sub(r"\ \-\ $", '', thread.css('.lastpost > a > span::text')[1].extract()),
                        "lastReplyLink": thread.css('.lastpost > a:nth-child(2)::attr(href)')[1].extract(),
                        "lastReplyTime": thread.css('.lastpost span:nth-child(3)::text')[1].extract(),
                    }
                    print('Thread {} processed...'.format(i))

                except ValueError as e:
                    print('Thread {} encountering...\n\t{}'.format(i,e))

        return forumsItem

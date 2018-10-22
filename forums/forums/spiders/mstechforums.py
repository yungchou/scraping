from scrapy import Spider, Request
from forums.items import ForumsItem
import re

class MstechforumsSpider(Spider):
    name = 'mstechforums'
    allowed_urls = ['https://social.technet.microsoft.com/']
    start_urls = ['https://social.technet.microsoft.com/Forums/en-us/home?sort=lastpostdesc&brandIgnore=true&page=1']
    custoem_settings = { 'LOG_LEVEL': 'ERROR'}

    def parse(self, response):

        self.log('\n\n{}\n\t\tSCRAPING STARTED\n{}\n'.format('-'*50,'-'*50))

        startThread, threadPerPage, totalThreads = \
            map(lambda x: int(x), re.findall('\d+',response.css('.itemSpan::text').extract_first()))
        
        totalPages = int(totalThreads)//int(threadPerPage) + 1
        #-------------------------------------------------------------------
        # After the above coding is done, at test time it turned out that
        # site will display 10,000 threads or 500 pages most. Although on
        # page 500, it will still show the 'Next >' at the bottom and clickable.
        # When accessing page 501 and beyond, it results with the follow error:
        # 'The search service is down. Please link directly to threads and come back later.'
        # Hence, here set the last page to 500.
        totalPages = 500
        #-------------------------------------------------------------------
        
        target_urls = [
            'https://social.technet.microsoft.com/Forums/en-us/home?sort=lastpostdesc&brandIgnore=true&page={}'\
            .format(x) for x in range(2,totalPages+1)  # start from the next page to totalPages
            ]

        for url in target_urls[:4]:  # test scraping for 4 pages
#        for url in target_urls:
            self.log('Yielding {}\n'.format(url))
            yield Request(url=url, callback=self.parse_the_page)

        self.log('\n{}\n\t\tSCRAPING ENDED\n{}\n\n'.format('-'*50,'-'*50))
        
    def parse_the_page(self, response):

        #threadsForThisPage = response.css('.detailscontainer > h3')

        #nextClick = response.css('#threadPager_Next::text').extract_first()
        # when needed, if nextClick: here

        threadFilter = re.sub('\s', '', \
            (re.sub(r'\r\n','',response.css('.selectedOption::text')[0].extract())))
        sortBy = re.sub('\s', '', \
            (re.sub(r'\r\n','',response.css('.selectedOption::text')[1].extract())))

        forumsItem = ForumsItem()
        forumsItem = {

            'votes': int((re.findall('\d+', response.css('div.votes div::text')[0].extract()))[0]),
            'threadState': response.css('.metrics.smallgreytext > span.statefilter > a::text')[0].extract(),
            'replyCount': int((re.findall('\d+', response.css('.replycount::text')[0].extract()))[0]),
            'viewCount': int((re.findall('\d+', response.css('.viewcount::text')[0].extract()))[0]),

            'threadTitle': response.css('.detailscontainer > h3 >a::text')[0].extract(),
            'threadTitleLink': response.css('.detailscontainer > h3 >a::attr(href)').extract_first(),
            'threadSummary': response.css('.threadSummary::text')[0].extract(),

            'createdByName': re.sub(r"\ \-\ $", '', response.css('.lastpost > a > span::text')[0].extract()),
            'createdByLink': response.css('.lastpost a:nth-child(2)::attr(href)')[1].extract(),
            'createdByTime': response.css('.lastpost span:nth-child(3)::text')[0].extract(),

            'lastReplyName': re.sub(r"\ \-\ $", '', response.css('.lastpost > a > span::text')[1].extract()),
            'lastReplyLink': response.css('.lastpost > a:nth-child(2)::attr(href)')[1].extract(),
            'lastReplyTime': response.css('.lastpost span:nth-child(3)::text')[1].extract()

        }

        yield forumsItem 

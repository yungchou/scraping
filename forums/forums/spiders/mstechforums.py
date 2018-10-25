from scrapy import Spider, Request
from forums.items import ForumsItem
import re

from datetime import datetime   # for housekeeping

class MstechforumsSpider(Spider):

  spider = {}    # for housekeeping

  name            = spider['name'] = 'mstechforums'
  allowed_urls    = spider['allow_urls'] = ['https://social.technet.microsoft.com/']
  start_urls      = spider['start_urls'] = ['https://social.technet.microsoft.com/Forums/en-US/home']
  custom_settings = spider['custom_settings'] = { 'LOG_LEVEL': 'ERROR'}
  print('{}\n{}'.format('*'*50, spider))

  def parse(self, response):

    crawl = {}  # for housekeeping

    startThread, threadsPerPage, totalThreads = \
      map(lambda x: int(x), re.findall('\d+',response.css('.itemSpan::text').extract_first()))

    crawl['startThread'] = startThread
    crawl['threadsPerPage'] = threadsPerPage
    crawl['totalThreads'] = totalThreads

    totalPages = crawl['totalPages'] = int(totalThreads)//int(threadsPerPage) + 1

    #-------------------------------------------------------------------
    # After the above coding is done, at test time it turned out that
    # site will display 10,000 threads or 500 pages most. Although on
    # page 500, it will still show the 'Next >' at the bottom and clickable.
    # When accessing page 501 and beyond, it results with the follow error:
    # 'The search service is down. Please link directly to threads and come back later.'
    # Hence, here set the last page to 500.

    # totalPages = crawl['totalPages'] = 100
    totalPages = crawl['totalPages'] = 500
    print('Hard-coded Total Pages to {} due to an identified constraint of the site.'.format(totalPages))
    #-------------------------------------------------------------------

    target_urls = [
      'https://social.technet.microsoft.com/Forums/en-us/home?sort=lastpostdesc&brandIgnore=true&page={}'\
      .format(x) for x in range(1,totalPages+1)  # start from the next page to totalPages
      ]

    print('\nC R A W L I N G ... :-P\n{}\n\n'.format(crawl))

    for url in target_urls:
      print('\nYielding to the page...{}'.format(url))
      yield Request(url=url, callback=self.parse_threadblock)

    print('\nC R A W L E D !!!  :-)')

  def parse_threadblock(self,response):

    # not use at this time
    threadFilter = re.sub('\s', '', \
      (re.sub(r'\r\n','',response.css('.selectedOption::text')[0].extract())))
    sortBy = re.sub('\s', '', \
      (re.sub(r'\r\n','',response.css('.selectedOption::text')[1].extract())))

    forumsItem = ForumsItem()

    for thread in response.css('.threadblock'):
      print('\n\tScraping the thread...{}'.format(thread))
      try:
        forumsItem = {

          'threadTitle': thread.css('.detailscontainer > h3 >a::text')[0].extract(),
          'threadTitleLink': thread.css('.detailscontainer > h3 >a::attr(href)').extract_first(),
          'threadSummary': thread.css('.threadSummary::text')[0].extract(),

          'category': response.css('div.EyebrowElement > a#categoryBreadcrumb > span::text').extract_first(),
          'categoryLink': response.css('div.EyebrowElement >a#categoryBreadcrumb::attr(href)').extract_first(),
          'subCategory': response.css('div.EyebrowElement.forumBreadcrumb > a > span::text').extract_first(),
          'subCategoryLink': response.css('div.EyebrowElement.forumBreadcrumb >a::attr(href)').extract_first(),

          'votes': int((re.findall('\d+', thread.css('div.votes div::text')[0].extract()))[0]),
          'threadState': thread.css('.metrics.smallgreytext > span.statefilter > a::text')[0].extract(),
          'replyCount': int((re.findall('\d+', thread.css('.replycount::text')[0].extract()))[0]),
          'viewCount': int((re.findall('\d+', thread.css('.viewcount::text')[0].extract()))[0]),

          'createdByName': re.sub(r"\ \-\ $", '', thread.css('.lastpost > a > span::text')[0].extract()),
          'createdByLink': thread.css('.lastpost a:nth-child(2)::attr(href)').extract(),
          'createdByTime': thread.css('.lastpost span:nth-child(3)::text').extract(),

          'lastReplyName': re.sub(r"\ \-\ $", '', thread.css('.lastpost > a > span::text')[0].extract()),
          'lastReplyLink': thread.css('.lastpost > a:nth-child(2)::attr(href)')[0].extract(),
          'lastReplyTime': thread.css('.lastpost span:nth-child(3)::text')[0].extract()

        }
        # print(forumsItem)
        yield forumsItem
        print('\n\tYielded...')

      except Exception as e:
        print('Oh, well...{}\n{}'.format('>'*20, e))

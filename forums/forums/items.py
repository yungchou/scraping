import scrapy

class ForumsItem(scrapy.Item):

    votes = scrapy.Field()
    threadState = scrapy.Field()
    replyCount = scrapy.Field()
    viewCount = scrapy.Field()

    threadTitle = scrapy.Field(),
    threadTitleLink = scrapy.Field(),
    threadSummary = scrapy.Field(),

    createdByName = scrapy.Field(),
    createdByLink = scrapy.Field(),
    createdByTime = scrapy.Field(),
    
    lastReplyName = scrapy.Field(),
    lastReplyLink = scrapy.Field(),
    lastReplyTime = scrapy.Field(),

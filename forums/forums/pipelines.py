import sqlite3

class ForumsPipeline(object):

    def open_spider(self, spider):

        self.conn = sqlite3.connect('mstechforums.sqlite')
        self.cur = self.conn.cursor()

        self.cur.execute('create table if not exists mstechforums(votes int, threadState varchar(30), replyCount int, viewCount int, threadTitle varchar(256), threadTitleLink text, threadSummary text, createdByName varchar(30), createdByLink text, createdByTime varchar(100), lastReplyName varchar(30), lastReplyLink text, lastReplyTime varchar(100))')
#        self.cur.execute('create table if not exists mstechforums(votes varchar(30), threadState varchar(30), replyCount varchar(30), viewCount varchar(30), threadTitle varchar(30), threadTitleLink text, threadSummary text, createdByName varchar(30), createdByLink text, createdByTime varchar(100), lastReplyName varchar(30), lastReplyLink text, lastReplyTime varchar(100))')

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        col = ','.join(item.keys())
        placeholder = ','.join(len(item)*'?')
#        print('\n{}\n{}\n{}\n{}\n'.format('+'*50,col,placeholder,'+'*50))    

        sql = 'insert into mstechforums({}) values({})'
        self.cur.execute(sql.format(col, placeholder), item.values())

        print('\n{}\nProcessed an item\n{}\n'.format('*'*50,'*'*50))
        return item

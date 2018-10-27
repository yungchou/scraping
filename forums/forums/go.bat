echo off
cls
REM scrapy crawl mstechforums >> msdnforums.log -o z.json -t json -s JOBLIB=scrapit
scrapy crawl mstechforums >> msdnforums.log -o msdnforums.csv -t csv -s JOBLIB=scrapit
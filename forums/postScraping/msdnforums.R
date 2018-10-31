rm(list=ls())
setwd('N:/dnd-webscraping/forums/postScraping')

library(dplyr)
library(mosaic)
library(stringr) # Ref: https://sebastiansauer.github.io/dplyr_filter/
library(plotly)
library(ggplot2)

# Original data file
forums <- read.csv(file='msdnforums.csv')

dim(forums)
str(forums) # Notice that createdByTime and lastReplyTime are stored as Factor.
sum(is.na(forums))  # Any missing values?

names(forums)
forums <- subset(forums,select=c("category","subCategory","threadState",
         "replyCount","viewCount","votes",
         "createdByTime", "lastReplyTime"))

# Convert createdByTime and lastReplyTime to standard datetime format
forums <- forums %>%
  mutate(createdByTime = as.character(createdByTime)) %>%
  mutate(lastReplyTime = as.character(lastReplyTime))

# A utc timestamp, logged at the web-scraping applicaiton start-time, is
# placed in the 1st line of the output log for serving as a replacement
# for those rows with non-standard representations of time.
ts <- read.table(file="msdnforums.log",nrows=1)

# When an entry is created or updated within the last 24 hours,
# non-standard representations of time indicating how many minutes ago,
# as shown here.
forums$createdByTime[str_detect(forums$createdByTime, "minutes ago$")] = ts
head(forums$createdByTime)
forums$lastReplyTime[str_detect(forums$lastReplyTime, "minutes ago$")] = ts
head(forums$lastReplyTime)

# Convert to standard datatime format
forums <- forums %>%
  mutate(createdByTime = as.Date(as.character(createdByTime), '%A, %B %d, %Y %I:%M %p' )) %>%
  mutate(lastReplyTime = as.Date(as.character(lastReplyTime), '%A, %B %d, %Y %I:%M %p' ))



plot(forums$createdByTime,forums$viewCount)
plot(forums$createdByTime,log(forums$votes))
plot(forums$createdByTime,log(forums$viewCount))
plot(forums$createdByTime,log(forums$replyCount))

ggplot(forums, aes(
  x=forums$category, y=forums$votes )) +
  geom_point() +  geom_jitter() + theme_bw() +
  geom_smooth(method=lm)

color=c(forums$viewCount,forums$replyCount)

names(forums)

str(forums)
summary(forums[c('category','subCategory')])
#fix(forums)
# Missing values

# Correlation
cor(forums$viewCount,forums$votes)
cor(forums$viewCount,forums$replyCount)
cor(forums$replyCount,forums$votes)

# Combined
answered <- subset(forums, threadState=='Answered',
               select=c('category','subCategory','threadState'))
threadState <- subset(forums, select=c('category','threadState'))
plot(tally(~category, data=threadState, margin=TRUE))
plot(tally(~category, data=answered, margin=TRUE))

# Categorical features
# mosaic, margin=TRUE provides the count, format= 'perc'/'prop'
tally(~threadState, data=forums, margin=TRUE)

# Contingency Tables
tally(~threadState+category, data=forums, margin=TRUE)

# Conditional Tables
tally(~threadState|subCategory=='Windows IoT', data=forums, margin=TRUE)

# Continuous features
# min, max, mean, favstats
mean(~viewCount, data=forums, na.rm=TRUE)
favstats(~viewCount, data=forums)

forums.sub3 <- subset(forums, select=c('viewCount','votes'))
dfapply(forums.sub3, favstats)


library(plotly)
#f1 <- subset(forums,threadState!='Discussion') %>% na.omit()
f1 <- forums
f1$threadState[which(f1$threadState == 1)] <- 'Answered'
f1$threadState[which(f1$threadstate == 2)] <- 'Proposed'
f1$threadState[which(f1$threadstate == 3)] <- 'Unanswered'
f1$threadState[which(f1$threadstate == 4)] <- 'Discussion'
f1$threadState <- as.factor(f1$threadState)

p <- plot_ly(f1,
             y = ~log(viewCount), x = ~log(replyCount), z = ~log(votes),
             color = ~threadState, colors = c('#BF382A', '#0C4B8E')) %>%
  add_markers() %>%
  layout(scene = list(yaxis = list(title = 'log-viewCount(y)'),
                      xaxis = list(title = 'log-replyCount(x)'),
                      zaxis = list(title = 'log-votes(z)')))

p

# relationship among views, votes and reply
summary(forums$viewCount, forums$votes, forums$replyCount)
summary(forums$viewCount, forums$votes)
cor(forums$viewCount, forums$votes)

summary(forums$viewCount, forums$replyCount)
cor(forums$viewCount, forums$replyCount)

summary(forums$votes, forums$replyCount)
cor(forums$votes, forums$replyCount)


library(mosaic)
tally(~vireCount, data=forums, margin=TRUE)


#######
#Cleaning up the column names so that there are no spaces.
names(forums)

# viewCount and replyCount
vcrc = subset(forums, select=(c('viewCount','replyCount', 'threadState')))

plotvcrc <- plot_ly(vcrc, x=log(vcrc$viewCount),y=log(vcrc$replyCount),
      #       type='scatter', mode='lines',
             color = ~threadState, colors = c('#BF382A', '#0C4B8E')) %>%
  add_markers() %>%
  layout(title ='replyCount vs. viewCount',
         xaxis = list(title='log-viewCount'),
         yaxis = list(title='log-replyCount'))
plotvcrc

# viewCount and votes
vcv = subset(forums, select=(c('viewCount','votes','threadState')))

plotvcv <- plot_ly(vcv, x=log(vcv$viewCount),y=log(vcv$votes),
             #       type='scatter', mode='lines',
             color = ~threadState, colors = c('#BF382A', '#0C4B8E')) %>%
  add_markers() %>%
  layout(title ='votes vs. viewCount',
         xaxis = list(title='log-viewCount'),
         yaxis = list(title='log-votes'))
plotvcv

# replyCount and votes
rcv = subset(forums, select=(c('replyCount','votes','threadState')))

plotrcv <- plot_ly(rcv, x=log(rcv$replyCount),y=log(rcv$votes),
                   #       type='scatter', mode='lines',
                   color = ~threadState, colors = c('#BF382A', '#0C4B8E')) %>%
  add_markers() %>%
  layout(title ='votes vs. replyCount',
         xaxis = list(title='log-replyCount'),
         yaxis = list(title='log-votes'))
plotrcv


# All three
vcrcv = subset(forums, select=(c('viewCount','replyCount','votes', 'threadState')))
#Creating a view density variable.
vcrcv[,4] = (vcrcv$viewCount)/vcrcv$votes
colnames(vcrcv)[4] = "viewCount/votes"

#Basic numerical EDA for forums dataset
summary(vcrcv)
sapply(vcrcv, sd)
cor(vcrcv)
plot(vcrcv)

#-------------------
# Linear Regression
#-------------------
vc <- forums$viewCount
rc <- forums$replyCount
v  <- forums$votes

LR <- lm( v ~ log(vc), data=vcrcv)

LR_summary <- summary(LR)
summary(LR)$coefficients
b0 = (summary(LR)$coefficients[1,1])
b1 = (summary(LR)$coefficients[2,1])
b01=toString(b0)



names(LR)
names(LR_summary)

coef3 <- reg$coefficients[3] # the 3rd values of coefficients
residuals <- forums$residuals





import re
import urllib
import urllib2
import time
import types
import page
import mysql
import sys
from bs4 import BeautifulSoup


class Spider:
    
    def __init__(self):
        self.page_num = 1
        self.total_num = None
        self.page_spider = page.Page()
        self.mysql = mysql.Mysql()

    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]',time.localtime(time.time()))

    def getCurrentDate(self):
        return time.strftime('%Y-%m-%d',time.localtime(time.time()))
    
    def getPageURLByNum(self, page_num):
        page_url = "http://iask.sina.com.cn/c/978-all-" + str(page_num) + ".html"
        return page_url

    def getPageByNum(self, page_num):
        request = urllib2.Request(self.getPageURLByNum(page_num))
        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print self.getCurrentTime(), "Loading page failed, code: ", e.code
                return None
            if hasattr(e, "reason"):
                print self.getCurrentTime(), "Loading page failed, reason: ", e.reason
                return None
        else:
            page = response.read().decode('utf-8')
            return page
                
    def getTotalPageNum(self):
        print self.getCurrentTime(), "Now getting the number of pages, please wait"
        page = self.getPageByNum(1)
        pattern = re.compile(u'<span class="more".*?>.*?<span.*?<a href.*?class="">(.*?)</a>\s*<a.*?\u4e0b\u4e00\u9875</a>', re.S)
        match = re.search(pattern, page)
        if match:
            return match.group(1)
        else:
            print self.getCurrentTime(), "Gettingg number of pages failed"

    def getQuestionInfo(self, question):
        if not type(question) is types.StringType:
            question = str(question)
        pattern = re.compile(u'<span.*?question-face.*?>.*?<img.*?alt="(.*?)".*?</span>.*?<a href="(.*?)".*?>(.*?)</a>.*?answer_num.*?>(\d*).*?</span>.*?answer_time.*?>(.*?)</span>', re.S)
        match = re.search(pattern, question)
        if match:
            author = match.group(1)
            href = match.group(2)
            text = match.group(3)
            ans_num = match.group(4)
            time = match.group(5)
            time_pattern = re.compile('\d{4}\-\d{2}\-\d{2}', re.S)
            time_match = re.search(time_pattern, time)
            if not time_match:
                time = self.getCurrentDate()
            return [author, href, text, ans_num, time]
        else:
            return None

    def getQuestions(self, page_num):
        page = self.getPageByNum(page_num)
        soup = BeautifulSoup(page)
        questions = soup.select("div.question_list ul li")
        for question in questions:
            info = self.getQuestionInfo(question)
            if info:
                url = "http://iask.sina.com.cn/" + info[1]
                ans = self.page_spider.getAnswer(url)
                print self.getCurrentTime(), "Now crawling ", page_num, " content", " and found a problem: ", info[2], "number of answers: ", info[3]
                ques_dict = {
                            "text": info[2],
                            "questioner": info[0],
                            "date": info[4],
                            "ans_num": info[3],
                            "url": url}
                insert_id = self.mysql.insertData("iask_questions",ques_dict)
                good_ans = ans[0]
                print self.getCurrentTime(), "Save to database, the id of the problem is: ", insert_id
                if good_ans:
                    print self.getCurrentTime(), insert_id, "exists good answer", good_ans[0]
                    good_ans_dict = {
                            "text": good_ans[0],
                            "answerer": good_ans[1],
                            "date": good_ans[2],
                            "is_good": str(good_ans[3]),
                            "question_id": str(insert_id)
                            }
                    if self.mysql.insertData("iask_answers",good_ans_dict):
                        print self.getCurrentTime(), "Best answer saved"
                    else:
                        print self.getCurrentTime(), "Fail to save best answer"
                other_anses = ans[1]
                for other_ans in other_anses:
                    if other_ans:
                        print self.getCurrentTime(), insert_id, " exists other answers ", other_ans[0]
                        other_ans_dict = {
                                "text": other_ans[0],
                                "answerer": other_ans[1],
                                "date": other_ans[2],
                                "is_good": str(other_ans[3]),
                                "question_id": str(insert_id)
                                }
                        if self.mysql.insertData("iask_answers",other_ans_dict):
                            print self.getCurrentTime(), "Other answeres saved"
                        else:
                            print self.getCurrentTime(), "Fail to save other answeres"

    def main(self):
        f_handler = open('out.log', 'w')
        sys.stdout = f_handler
        page = open('page.txt', 'r')
        content = page.readline()
        start_page = int(content.strip()) - 1
        page.close()
        print self.getCurrentTime(), "Starting page", start_page
        print self.getCurrentTime(), "Web crawler is starting, crawles Aiwen"
        self.total_num = self.getTotalPageNum()
        print self.getCurrentTime(), "Get the number of pages: ", self.total_num
        if not start_page:
            start_page = int(self.total_num)
        for x in range(1, start_page):
            print self.getCurrentTime(), "Now crawling the ", start_page-x+1, "page"
            try:
                self.getQuestions(start_page-x+1)
            except urllib2.URLError, e:
                if hasattr(e, "reason"):
                    print self.getCurrentTime(), "Extract info failed, reason: ", e.reason
            except Exception, e:
                print self.getCurrentTime(), "Extract info failed, reason: ", e
            if start_page-x+1 < start_page:
                f = open('page.txt', 'w')
                f.write(str(start_page-x+1))
                print self.getCurrentTime(), "Writing new page: ", start_page-x+1
                f.close()


spider = Spider()
spider.main()

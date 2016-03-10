import MySQLdb
import time


class Mysql:

    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]',time.localtime(time.time()))

    def __init__(self):
        try:
            self.db = MySQLdb.connect(host="localhost", user="root", passwd="1221", db="aiwen")
            # create a Cursor object, to let you execute all the queries you need
            self.cur = self.db.cursor()
        except MySQLdb.Error, e:
            print self.getCurrentTime(), "Connecting database failed, reason %d: %s" % (e.args[0], e.args[1])

    def insertData(self, table, my_dict):
        try:
            self.db.set_character_set('utf8')
            cols = ', '.join(my_dict.keys())
            values = '"," '.join(my_dict.values())
            sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, cols, '"'+values+'"')
            try:
                result = self.cur.execute(sql)
                insert_id = self.db.insert_id()
                self.db.commit()
                if result:
                     return insert_id
                else:
                     return 0
            except MySQLdb.Error, e:
                self.db.rollback()
                if "key 'PRIMARY'" in e.args[1]:
                    print self.getCurrentTime(), "Data already exists, did not insert data"
                else:
                    print self.getCurrentTime(), "Data insertion failed reason %d: %s" % (e.args[0], e.args[1])
        except MySQLdb.Error, e:
            print self.getCurrentTime(), "something wrong with database, the reason%d: %s" % (e.args[0], e.args[1])
            

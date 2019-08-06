import pickle
import sys
import time

from func_timeout import func_set_timeout, FunctionTimedOut
import requests
import json

# person is a dict to store the id to name
# person_spidered is the set to store the name that has been spidered
# person_unspider is the set to store the name that has not been spidered
base_url = 'https://www.sogou.com/kmap?query='
postfix = '&from=relation&id='
person = dict()
person_spidered = set()
person_unspider = set()


def funtime(func):
    '''
    This decarator is used for timing
    :param func: the funtion you want to time.
    :return:
    '''
    def wrapper(*args, **kw):
        local_time = time.time()
        tmp = func(*args, **kw)
        print("current Function [%s] run time is %.6f" % (func.__name__, (time.time() - local_time)))
        return tmp

    return wrapper


class Spider:
    @funtime
    def parse_one_page(self, response):
        '''
        parse the response and store the infomation into the .txt
        :param response: the http response
        :return:
        '''
        if response.text.__contains__('਍'):
            text = response.text.replace('਍', '')
        j = json.loads(text)
        with open('name2id.txt', 'a+', encoding='utf-8') as f:
            for i in j['nodes']:

                if i['id'] not in person.keys():
                    person[i['id']] = i['name']
                    f.write(i['id'] + "\t" + i['name'] + '\n')
                if i['name'] not in person_spidered:
                    person_unspider.add(i['name'])

        with open('name_intro.txt', 'a+', encoding='utf-8') as f:
            item = j['nodes'][0]
            if 'intro' in item.keys():
                f.write(item['id'] + "\t" + item['name'] + "\t" + item['intro'] + '\n')

        with open('relation.txt', 'a+', encoding='utf-8') as f:
            for i in j['links']:
                f.write(
                    person.get(i['from']) + "\t" + person.get(i['to']) + "\t" + i['name'] + "\t" + str(i['type']) + "\n")

    # this decorator is usful because it can raise an exception when the function overran
    @func_set_timeout(2)
    @funtime
    def spider_name(self, name):
        '''

        :param name: the name of the person to be spidered
        :return:
        '''
        url = base_url + name + postfix
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36',
                'Cookie': 'ABTEST=3|1564648758|v17; IPLOC=JP; SUID=677BC7342113940A000000005D42A536; SUV=1564648795913366; browerV=3; osV=1'
            }
            response = requests.get(url, headers=headers, timeout=5)
            self.parse_one_page(response)
            person_spidered.add(name)
        except Exception as e:
            print(e)

    @funtime
    def run_spider_name(self, name):
        '''
        this function mains to catch the FunctionTimedOut Exception raised by func spider_name()
        :param name:
        :return:
        '''
        global headers
        try:
            self.spider_name(name)
        except FunctionTimedOut:
            dumpToPkl()
            print("dump done")
            sys.exit(0)
        except Exception as e:
            print(e)


@funtime
def dumpToPkl():
    '''dump the person dict, person_spidered set and person_unspider to the pkl'''
    with open('data/person.pkl', 'wb') as f:
        pickle.dump(person, f)
    with open('data/person_spidered.pkl', 'wb') as f:
        pickle.dump(person_spidered, f)
    with open('data/person_queue.pkl', 'wb') as f:
        pickle.dump(person_unspider, f)


@funtime
def loadFromPkl():
    '''

    :return:
    '''
    # the usage of global, which refer to the global variable
    global person_spidered, person, person_unspider
    with open('data/person.pkl', 'rb') as f:
        person = pickle.load(f)
    with open('data/person_spidered.pkl', 'rb') as f:
        person_spidered = pickle.load(f)
    with open('data/person_queue.pkl', 'rb') as f:
        person_unspider = pickle.load(f)


if __name__ == '__main__':
    person_unspider.add("许志安")
    count = 0
    a = Spider()
    loadFromPkl()
    while len(person_unspider) > 0:
        name = person_unspider.pop()
        print(name)
        a.run_spider_name(name)
        person_spidered.add(name)
        count += 1
        print(count)
        print('\n')


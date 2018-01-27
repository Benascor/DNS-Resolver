import sys
import dns.message
import dns.query
import dns.name
import dns.resolver
import time

#Classes
class MyResolver():
    def __init__(self):
        self.referralcache = {'a.root-servers.net' : {'A' : '198.41.0.4', 'AAAA' : '2001:503:ba3e::2:30'}}
        self.answercache = {}

    def resolve(self, domainName, recordType, dnsname):
        #Check if we already know the answer
        if domainName in self.answercache:
            if recordType in self.answercache[domainName]:
                #We do! return it!
                print("_____________________________________________________\n")
                print("*** Fetching ", domainName, recordType, " from cache.")
                print(self.answercache[domainName][recordType], '\n')
                print("_____________________________________________________\n")
                return self.answercache[domainName][recordType]
        
        #We don't know the answer
        if dnsname == 'root':
            domainmod = domainName.rstrip('.')
            dot = domainmod.rfind('.')
            tld = domainmod[dot+1:] + '.'
            response = ""
            if domainName in self.referralcache:
                if 'NS' in self.referralcache[domainName]:
                    print("*** Fetching nameserver ", self.referralcache[domainName]['NS'][0]," for ",domainName, " from the cache.")
                    query = dns.message.make_query(domainName, recordType)
                    newdnsname = self.referralcache[tld]['NS'][0]
                    if 'A' in self.referralcache[newdnsname]:
                        newdns = self.referralcache[newdnsname]['A']
                    else:
                        newdns = self.referralcache[newdnsname]['AAAA']
                    try:
                        response = dns.query.udp(query, newdns, timeout = 5.0)
                    except Exception:
                        print("_____________________________________________________\n")
                        print("*** QUERY ", domainName, " for RRType ", recordType)
                        print("None\n")
                        print("_____________________________________________________\n")
                        return "None"
        
            elif tld in self.referralcache:
                if 'NS' in self.referralcache[tld]:
                    print("*** Fetching nameserver ", self.referralcache[tld]['NS'][0]," for ",tld ," from the cache.")
                    query = dns.message.make_query(domainName, recordType)
                    newdnsname = self.referralcache[tld]['NS'][0]
                    if 'A' in self.referralcache[newdnsname]:
                        newdns = self.referralcache[newdnsname]['A']
                    else:
                        newdns = self.referralcache[newdnsname]['AAAA']
                    try:
                        response = dns.query.udp(query, newdns, timeout = 5.0)
                    except Exception:
                        print("_____________________________________________________\n")
                        print("*** QUERY ", domainName, " for RRType ", recordType)
                        print("None\n")
                        print("_____________________________________________________\n")
                        return "None"
            else:
                query = dns.message.make_query(domainName, recordType)
                try:
                    response = dns.query.udp(query, self.referralcache['a.root-servers.net']['A'], timeout = 5.0)
                except Exception:
                    print("_____________________________________________________\n")
                    print("*** QUERY ", domainName, " for RRType ", recordType)
                    print("None\n")
                    print("_____________________________________________________\n")
                    return "None"
            nextdns = ""
            for ans in response.answer:
                split = ans.to_text()
                if split[0].rstrip('.') == domainName:
                    if split[3] == recordType:
                        if domainName not in self.answercache:
                            self.answercache[domainName] = {}
                        self.answercache[domainName][recordType] = response
                        print("_____________________________________________________\n")
                        print("*** QUERY ", domainName, " for RRType ", recordType)
                        print(response, '\n')
                        print("_____________________________________________________\n")
                        return response
            for auth in response.authority:
                split = auth.to_text().split('\n')
                for line in split:
                    lis = line.split(' ')
                    if lis[0] in self.referralcache:
                        if lis[3] in self.referralcache[lis[0]]:
                            self.referralcache[lis[0]][lis[3]].append(lis[4])
                        else:
                            self.referralcache[lis[0]][lis[3]] = [lis[4]]
                    else:
                        self.referralcache[lis[0]] = {}
                        self.referralcache[lis[0]][lis[3]] = [lis[4]]
            if not response.additional:
                if domainName not in self.answercache:
                    self.answercache[domainName] = {}
                self.answercache[domainName][recordType] = response
                print("_____________________________________________________\n")
                print("*** QUERY ", domainName, " for RRType ", recordType)
                print(response, '\n')
                print("_____________________________________________________\n")
                return response
            for addi in response.additional:
                split = addi.to_text().rstrip().split(' ')
                self.referralcache[split[0]] = {}
                self.referralcache[split[0]][split[3]] = split[4]
                nextdns = split[0]
            print(response, '\n')
            return self.resolve(domainName, recordType, nextdns)
        else:
            query = dns.message.make_query(domainName, recordType)
            if('A' in self.referralcache[dnsname]):
                try:
                    response = dns.query.udp(query, self.referralcache[dnsname]['A'], timeout = 5.0)
                except Exception:
                    print("_____________________________________________________\n")
                    print("*** QUERY ", domainName, " for RRType ", recordType)
                    print("None\n")
                    print("_____________________________________________________\n")
                    return "None"
            else:
                try:
                    response = dns.query.udp(query, self.referralcache[dnsname]['AAAA'], timeout = 5.0)
                except Exception:
                    print("_____________________________________________________\n")
                    print("*** QUERY ", domainName, " for RRType ", recordType)
                    print("None\n")
                    print("_____________________________________________________\n")
                    return "None"
            nextdns = ""
            for ans in response.answer:
                split = ans.to_text().split(' ')
                if split[0] == domainName:
                    if split[3] == recordType:
                        if domainName not in self.answercache:
                            self.answercache[domainName] = {}
                        self.answercache[domainName][recordType] = response
                        print("_____________________________________________________\n")
                        print("*** QUERY ", domainName, " for RRType ", recordType)
                        print(response, '\n')
                        print("_____________________________________________________\n")
                        return response
            for auth in response.authority:
                split = auth.to_text().split('\n')
                for line in split:
                    lis = line.split(' ')
                    if lis[0] in self.referralcache:
                        if lis[3] in self.referralcache[lis[0]]:
                            self.referralcache[lis[0]][lis[3]].append(lis[4])
                        else:
                            self.referralcache[lis[0]][lis[3]] = [lis[4]]
                    else:
                        self.referralcache[lis[0]] = {}
                        self.referralcache[lis[0]][lis[3]] = [lis[4]]
            if not response.additional:
                if domainName not in self.answercache:
                    self.answercache[domainName] = {}
                self.answercache[domainName][recordType] = response
                print("_____________________________________________________\n")
                print("*** QUERY ", domainName, " for RRType ", recordType)
                print(response, '\n')
                print("_____________________________________________________\n")
                return response
            for addi in response.additional:
                split = addi.to_text().rstrip().split(' ')
                if not split:
                    print("_____________________________________________________\n")
                    print("*** QUERY ", domainName, " for RRType ", recordType)
                    print(response, '\n')
                    print("_____________________________________________________\n")
                    return response
                self.referralcache[split[0]] = {}
                self.referralcache[split[0]][split[3]] = split[4]
                nextdns = split[0]
            print(response, '\n')
            return self.resolve(domainName, recordType, nextdns)
    
    def printcache(self):
        print("Answer Cache Contents:\n")
        for domain in self.answercache:
            print(domain, " :")
            for record in self.answercache[domain]:
                print(record, " : ", self.answercache[domain][record])
            print()
        print("Referral Cache Contents:\n")
        for domain in self.referralcache:
            print(domain, " :")
            for record in self.referralcache[domain]:
                print(record, " : ", self.referralcache[domain][record])
            print()

class Parser():
    def parse(self, filename):
        file = open(filename, "r")
        x = MyResolver()
        for line in file:
            print("\n***************************************************\n")
            print("COMMAND: ", line)
            splitLine = line.rstrip().split(' ')
            if splitLine[0] == 'resolve':
                start = time.time()
                x.resolve(splitLine[1] + '.', splitLine[2], 'root')
                end = time.time()
                print("Total latency: ", end - start)
            elif line.rstrip() == 'print cache':
                x.printcache()
            elif line == 'quit':
                print()
                print("Program terminated")
                exit()

#Main
p = Parser()
p.parse(sys.argv[1])
# I had 2 googles that I had to perform to do this project. Which is where the first 2 imports come from.
from itertools import combinations
from os import popen
from datetime import datetime
# Sometimes I think about importing these in the functions they're used in ...... not sure if that's egregious.
# but it makes some sense in my mind for a couple reasons


def arp():
    out = []  # os.popen is what came up when I googled:'python cmd output as var'
    arp_out = popen('arp -a').read()  # Good, I hated os.system('arp -a >> arp.txt')
    print(arp_out)  # then we turn it into a list matrix and can take out the whitespace and title lines in next bit:
    cmd_matrix = [[c for c in r.split(' ') if c != ''] for r in arp_out.split('\n') if r != '' and 'Intern' not in r]
    for line in cmd_matrix:
        if len(line) == 4:  # ["Interface:", "123.1.2.3", "---", "0x1"]
            interface_ip, interface_id = line[1::2]
        else:  # ["255.255.255.255", "ff-ff-ff-ff-ff-ff", "static"]
            ip_v4, mac, arp_type = line
            out.append([interface_ip, interface_id, ip_v4, mac, arp_type])
    return out if out else None


def mac_dupes(table):
    if table:
        out = []
        for c in combinations(table, 2):  # itertools.combinations() makes that trivial! no indexing required.
            # google:'python compare all items in list'
            if c[0][1] == c[1][1] and c[0][0] != c[1][0] and c[0][1] != "ff-ff-ff-ff-ff-ff":
                # if (mac1 == mac2) and (ip1 != ip2) and (mac1 != "ff-ff-ff-ff-ff-ff")
                print(c)  # https://docs.python.org/3/library/itertools.html#itertools.combinations
                out.append([c[0][1], c[0][0], c[1][0]])
        return out if out else None


def logger(dupe_list):
    if dupe_list:
        out = ''
        for match in dupe_list:
            out += f'Arp Spoofed!\nThe address is:{match[0]}\nDate:{datetime()}\n\n'
        with open("log.txt", 'a') as f:
            f.write(out)


def main():
    arp_res = arp()
    ip_mac = [i[2:4] for i in arp_res]
    logger(mac_dupes(ip_mac))
    input("press enter to close")


if __name__ == '__main__':
    main()

""" whats good.
------------------------------------------------------------------------------------------------------------------------
                 v-fifth(for)          v-sixth(if)
              v-third(look)            v         v-seven(look)                                                  v-fifth(look)
cmd_matrix = [[c for c in r.split(' ') if c != ''] for r in arp_out.split('\n') if r != '' and 'Intern' not in r]
^first       ^-second(look)                        ^-third(for)                 ^-fourth(if)                      ^-second(none)
               ^-seventh(c)
========================================================================================================================
#2 is none
cmd_matrix = [ ] #1, 2 implies no indent.
for row in arp_out.split('\n'): #between 3,4
    if row != '' and 'Intern' not in row: #between 4,5
        cmd_matrix.append([]) # implied by 3,5(look)
        for column in row.split(' '): #between 5,6
            if column != '': #between 6,7
                cmd_matrix[-1].append(column) #7. implies that you add x to the newest(last)list generation.
------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------
arp_out = popen('arp -a').read()
===================================
os.system('arp -a >> arp.txt')
file = open('arp.txt','r')
arp_out = file.read()
file.close()
------------------------------------------------------------
"""

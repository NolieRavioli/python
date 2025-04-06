# whats gooood


from datetime import datetime
from itertools import combinations
from os import popen
from re import sub
# Sometimes I think about importing these in the functions they're used in ...... not sure if that's egregious.

# I had 3 googles that i had to perform to do this project. datetime was pretty self-explanatory

def arp():
    # os.system('arp -a >> arp.txt') and opening that file to assign a variable seems like a lot.
    # os.popen is what came up when i googled:'python cmd output as var'
    # it turns out its literally to open a pipe to the command file object (with default 'r' mode.)
    out = []
    command_output = popen('arp -a').read().split('\n')
    command_output = [e for e in command_output if e != '' and 'Intern' not in e]  # gets rid of title lines/empty lines
    #print(command_output)
    for line in command_output:
        if line[:6] == 'Interf':
            # only pay attention to interface lines with if/else
            interface_ip, interface_id = line.split(' ')[1::2]
            continue

        # regular expression substitution, get rid of that whitespace. lots of ways to do it,
        # but I've never really used Reg Ex since learning more about it in this class.
        # I thought I would try that when the re module came up in my search:'python remove whitespace from str'.
        #line = " ".join(line.split())
        #line = sub(r' +', r' ', line).strip()
        # If we're being honest, I don't even need to do that anymore with my " if e != '' "
        ip_v4, mac, arp_type = [e for e in line.split(' ') if e != '']
        out.append([interface_ip, ip_v4, mac, arp_type, interface_id])
    if out:
        # just some checks that I added to all the functions for passive error checking
        return out


def mac_dupes(table):
    if table:
        out = []
        for c in combinations(table, 2):
            # itertools.combinations() makes that trivial! no indexing required.
            # I had to google:'python compare all items in list'
            #print(c)
            if c[0][1] == c[1][1] and c[0][0] != c[1][0] and c[0][1] != "ff-ff-ff-ff-ff-ff":
                out.append([c[0][1], c[0][0], c[1][0]])
        if out:
            return out


def logger(dupe_list):
    if dupe_list:
        out = ''
        for IPMATCH in dupe_list:
            out += f'Arp Spoofed!\nThe address is:{IPMATCH[0]}\nDate:{datetime.datetime()}\n\n'
            with open("log.txt", 'a') as f:
                f.write(out)


def main():
    arp_res = arp()
    ip_mac = [i[1:3] for i in arp_res]
    logger(mac_dupes(ip_mac))


if __name__ == '__main__':
    main()

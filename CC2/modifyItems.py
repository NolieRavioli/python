import hashlib
import struct
import tkinter as tk
from tkinter import ttk
import copy

fileToOpen = "dedicated_server.exe"

filesToOpen = ["dedicated_server.exe", "carrier_command.exe"]

names = ["Seal", "Walrus", "Bear", "Mule", "Albatross", "Manta", "Razorbill", "Petrel", "Barge", "Main Gun",
         "Main Gun 2", "20mm Chaingun", 'Rocket Pod', 'Virus Bots', 'CWIZ Turret', 'IR Missile Turret', 'Light Bomb',
         'Medium Bomb', 'Heavy Bomb', 'IR Missile', 'Laser Missile', 'AA Missile', 'Torpedo', 'Noisemaker',
         'Countermeasure', 'TV Missile', 'Observation Camera', 'Small Camera', 'Gimbal Camera', 'Actuated Camera',
         'AWACS', 'Fuel Tank', 'Flare Launcher', 'Battle Cannon', 'Heavy Cannon', 'Ground Artillery Cannon',
         'Ground Radar', 'Sonic Pulse Generator', 'Smoke Launcher (Stream)', 'Smoke Launcher (Explosive)', '30mm Ammo',
         '40mm Ammo', 'Cruise Missile', 'Rocket', 'Flare', '20mm Ammo', '100mm Ammo', '120mm Ammo', '160mm Ammo',
         'Fuel', 'Sonic Pulse Ammo', 'Smoke Ammo', 'CWIZ Needlefish', 'Torpedo Needlefish', '160mm Needlefish',
         'Cruise Missile Needlefish', '30mm Land Turret', 'CWIZ Land Turret', 'Missile Land Turret', 'Deployable Droid',
         '30mm Gimbal Turret']
items = [
    ["icon_chassis_16_wheel_small", 1, 5, 10000, 500, 0x78, 1, 10, 0x139, 0x13a],
    ["icon_chassis_16_wheel_medium", 2, 5, 15000, 0x2ee, 0x96, 1, 10, 0x13b, 0x13c],
    ["icon_chassis_16_wheel_large", 3, 5, 20000, 1000, 0xb4, 1, 10, 0x13d, 0x13e],
    ["icon_chassis_16_wheel_mule", 0x3a, 5, 20000, 0x2ee, 0x96, 1, 10, 0x5e0, 0x5e1],
    ["icon_chassis_16_wing_small", 4, 6, 20000, 1000, 0x78, 1, 10, 0x13f, 0x140],
    ["icon_chassis_16_wing_large", 5, 6, 25000, 0x4e2, 0xb4, 1, 10, 0x141, 0x142],
    ["icon_chassis_16_rotor_small", 6, 6, 15000, 0x2ee, 0x78, 1, 10, 0x143, 0x144],
    ["icon_chassis_16_rotor_large", 7, 6, 20000, 1000, 0xb4, 1, 10, 0x145, 0x146],
    ["icon_chassis_16_barge", 8, 8, 20000, 1000, 0xb4, 1, 10, 0x147, 0x148],
    ["icon_attachment_16_turret_main_gun", 9, 3, 5000, 200, 0x78, 1, 5, 0x149, 0x14a],
    ["icon_attachment_16_turret_main_gun_2", 0x2f, 3, 5000, 0xfa, 0x78, 1, 5, 0x288, 0x14a],
    ["icon_attachment_16_air_chaingun", 10, 3, 5000, 200, 0x78, 1, 5, 0x14b, 0x14c],
    ["icon_attachment_16_rocket_pod", 0xb, 3, 5000, 0xfa, 0x78, 1, 5, 0x14d, 0x14e],
    ["icon_attachment_16_turret_robots", 0x32, 4, 5000, 200, 0x3c, 1, 5, 0x16d, 0x150],
    ["icon_attachment_16_turret_ciws", 0xc, 3, 5000, 0xfa, 0x78, 1, 5, 0x151, 0x152],
    ["icon_attachment_16_turret_missile", 0xd, 3, 5000, 0xfa, 0x78, 1, 5, 0x153, 0x154],
    ["icon_attachment_16_air_bomb_1", 0xe, 2, 500, 10, 0x14, 1, 2, 0x156, 0x155],
    ["icon_attachment_16_air_bomb_2", 0xf, 2, 1000, 0x19, 0x1e, 1, 2, 0x157, 0x155],
    ["icon_attachment_16_air_bomb_3", 0x10, 2, 2000, 0x32, 0x28, 1, 2, 0x158, 0x155],
    ["icon_attachment_16_air_missile_1", 0x11, 2, 1000, 0x19, 0x28, 1, 2, 0x15b, 0x47a],
    ["icon_attachment_16_air_missile_2", 0x12, 2, 1000, 0x19, 0x28, 1, 2, 0x15c, 0x47b],
    ["icon_attachment_16_air_missile_4", 0x13, 2, 1000, 0x19, 0x28, 1, 2, 0x15e, 0x47c],
    ["icon_attachment_16_air_torpedo", 0x25, 2, 1000, 0x32, 0x50, 1, 2, 0x20e, 0x55a],
    ["icon_attachment_16_air_torpedo_noisemaker", 0x27, 2, 1000, 0x32, 0x50, 1, 2, 0x211, 0x55b],
    ["icon_attachment_16_air_torpedo_decoy", 0x28, 2, 1000, 0x32, 0x50, 1, 2, 0x213, 0x55c],
    ["icon_attachment_16_air_missile_tv", 0x26, 2, 2000, 100, 0x3c, 1, 2, 0x20c, 0x20d],
    ["icon_attachment_16_camera_large", 0x14, 4, 5000, 0x32, 0x3c, 1, 5, 0x165, 0x166],
    ["icon_attachment_16_small_camera", 0x15, 4, 0x9c4, 0x32, 0x3c, 1, 5, 0x161, 0x162],
    ["icon_attachment_16_camera_aircraft", 0x16, 4, 5000, 0x32, 0x3c, 1, 5, 0x163, 0x164],
    ["icon_attachment_16_small_camera_obs", 0x17, 4, 5000, 0x32, 0x3c, 1, 5, 0x15f, 0x160],
    ["icon_attachment_16_air_radar", 0x18, 4, 8000, 500, 0xb4, 1, 5, 0x167, 0x168],
    ["icon_attachment_16_air_fuel", 0x19, 4, 5000, 0x32, 0x28, 1, 5, 0x169, 0x16a],
    ["icon_attachment_16_small_flare", 0x1a, 3, 5000, 100, 0x1e, 1, 5, 0x16b, 0x16c],
    ["icon_attachment_16_turret_main_battle_cannon", 0x1b, 3, 6000, 0x2ee, 0x78, 1, 5, 0x16f, 0x58b],
    ["icon_attachment_16_turret_main_heavy_cannon", 0x31, 3, 6000, 0x2ee, 0x78, 1, 5, 0x289, 0x170],
    ["icon_attachment_16_turret_artillery", 0x1c, 3, 6000, 0x2ee, 0x78, 1, 5, 0x171, 0x172],
    ["icon_attachment_16_radar_golfball", 0x29, 4, 8000, 0xfa, 0x78, 1, 5, 0x280, 0x55d],
    ["icon_attachment_16_sonic_pulse_generator", 0x2a, 4, 0x9c4, 0xfa, 0x3c, 1, 5, 0x281, 0x281],
    ["icon_attachment_16_smoke_launcher_stream", 0x2b, 4, 0x9c4, 0x32, 0x3c, 1, 5, 0x283, 0x283],
    ["icon_attachment_16_smoke_launcher_explosive", 0x2c, 4, 0x9c4, 0x32, 0x3c, 1, 5, 0x282, 0x282],
    ["icon_item_16_ammo_30mm", 0, 1, 1, 1, 2, 100, 1, 0x135, 0x136],
    ["icon_item_16_ammo_40mm", 0x30, 1, 1, 2, 3, 100, 1, 0x287, 0x136],
    ["icon_item_16_ammo_cruise_missile", 0x1d, 2, 2000, 100, 0x3c, 1, 1, 0x175, 0x176],
    ["icon_item_16_ammo_rocket", 0x1e, 2, 0x32, 10, 10, 1, 1, 0x177, 0x178],
    ["icon_item_16_ammo_flare", 0x1f, 1, 10, 1, 10, 10, 1, 0x179, 0x17a],
    ["icon_item_16_ammo_20mm", 0x20, 1, 1, 1, 2, 100, 2, 0x17b, 0x17c],
    ["icon_item_16_ammo_100mm", 0x21, 1, 1, 5, 10, 100, 2, 0x17d, 0x17e],
    ["icon_item_16_ammo_120mm", 0x22, 1, 1, 0x14, 0x14, 100, 3, 0x17f, 0x180],
    ["icon_item_16_ammo_160mm", 0x23, 1, 1, 0x32, 0x1e, 100, 3, 0x181, 0x182],
    ["icon_item_16_fuel_barrel", 0x24, 7, 10, 10, 0x14, 1, 5, 0x183, 0x184],
    ["icon_item_16_ammo_sonic_pulse", 0x2d, 1, 10, 0x32, 0x14, 1, 1, 0x285, 0x285],
    ["icon_item_16_ammo_smoke", 0x2e, 1, 10, 1, 10, 1, 1, 0x286, 0x286],
    ["icon_chassis_16_ship_light", 0x33, 0, 75000, 6000, 0xb4, 1, 10, 0x5b5, 0x5bc],
    ["icon_chassis_16_ship_light", 0x34, 0, 75000, 10000, 0xb4, 1, 10, 0x5b6, 0x5bd],
    ["icon_chassis_16_ship_light", 0x35, 0, 75000, 8000, 0xb4, 1, 10, 0x5b7, 0x5be],
    ["icon_chassis_16_ship_light", 0x36, 0, 75000, 12000, 0xb4, 1, 10, 0x5b8, 0x5bf],
    ["icon_chassis_16_land_turret", 0x37, 9, 10000, 1000, 0x3c, 1, 1, 0x5d0, 0x5d3],
    ["icon_chassis_16_land_turret", 0x38, 9, 10000, 0x4e2, 0x3c, 1, 1, 0x5d1, 0x5d4],
    ["icon_chassis_16_land_turret", 0x39, 9, 10000, 0x5dc, 0x3c, 1, 1, 0x5d2, 0x5d5],
    ["icon_attachment_16_deployable_droid", 0x3b, 4, 5000, 500, 0x3c, 1, 5, 0x5ee, 0x5ef],
    ["icon_attachment_16_turret_gimbal", 0x3c, 3, 5000, 400, 0x78, 1, 5, 0x5f9, 0x5fa],
]


item_dict = {}
for name, item_data in zip(names, items):
    item_dict[name] = item_data
il2 = copy.deepcopy(item_dict)

def cs256(a):
    b = hashlib.sha256()
    with open(a, "rb") as f:
        while c := f.read(8192):
            b.update(c)
    print(b.hexdigest())
    return b.hexdigest()

def fo(exe_path, pattern_bytes, start=0, end=-1):
    offsets = []
    with open(exe_path, 'rb') as exe_file:
        exe_data = exe_file.read()
    offset = exe_data.find(pattern_bytes, start, end)
    while offset != -1:
        offsets.append(offset)
        offset = exe_data.find(pattern_bytes, offset + len(pattern_bytes), end)
    return offsets

hexDict = {}
for name in item_dict:
    out = ""
    a = item_dict[name][:1:-1]
    for h in a:
        if h >= 0x96:
            packed_bytes = struct.pack("<I", h)
            out += " 68 "
        else:
            packed_bytes = struct.pack("<B", h)
            out += " 6A "
        packed_str = ' '.join(format(byte, '02X') for byte in packed_bytes)
        out += packed_str
    hexDict[name] = out.strip()

offsetDict = {}
for name in hexDict:
    offsets = fo(fileToOpen, bytes.fromhex(hexDict[name].replace(" ", "")))
    if len(offsets) != 1:
        print(len(offsets), name, hexDict[name])
    else:
        offsetDict[name] = [offsets[0], [v for v in reversed(item_dict[name][1:])]]


class ItemEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Item Editor")

        self.iv = tk.StringVar(value="Select Item")
        self.idd = ttk.Combobox(root, textvariable=self.iv, values=names)
        self.idd.grid(row=0, column=0, padx=10, pady=10)
        self.idd.bind("<<ComboboxSelected>>", self.update_display)

        ns = ["Item ID", "Type ID", "Mass", "Build Cost", "Build Time", "Barge Pull Size", "Group ID", "IDK", "IDK also"]
        self.e = []

        for y, n in enumerate(ns, start=1):
            l = tk.Label(root, text=n)
            l.grid(row=y, column=0, padx=10, pady=5, sticky="e")
            ew = tk.Entry(root)
            ew.grid(row=y, column=1, padx=10, pady=5)
            self.e.append(ew)

        self.fv = tk.StringVar(value="dedicated_server.exe")
        self.fdd = ttk.Combobox(root, textvariable=self.fv, values=filesToOpen)
        self.fdd.grid(row=len(ns) + 1, column=0, padx=10, pady=10)
        self.fdd.bind("<<ComboboxSelected>>", self.offset_dict_generator)
        self.save = tk.Button(root, text="Save File", command=self.save_file)
        self.save.grid(row=len(ns) + 1, column=1, padx=10, pady=10)

        self.cv = {}
        self.li = None

    def offset_dict_generator(self, event):
        global offsetDict
        global item_dict
        offsetDict = {}

        for name in hexDict:
            offsets = fo(self.fv.get(), bytes.fromhex(hexDict[name].replace(" ", "")))
            if len(offsets) != 1:
                print(len(offsets), name, hexDict[name])
            else:
                offsetDict[name] = [offsets[0], [v for v in reversed(item_dict[name][1:])]]

    def update_display(self, event):
        si = self.iv.get()
        if not self.li:
            self.li = si
            for i, tx in enumerate(self.e):
                tx.insert(0, str(item_dict[si][i+1]))  # Access the value directly
        elif si in item_dict:
            c = {}
            for i, tx in enumerate(self.e, start=1):
                es = tx.get()
                tx.delete(0, tk.END)
                tx.insert(0, str(item_dict[si][i]))  # Access the value directly
                if es:
                    e = int(es)
                    if e != item_dict[self.li][i]:
                        item_dict[self.li][i] = e
                        c[self.li] = (i, e)
            self.cv.update(c)
        self.li = si

    def save_file(self):
        self.update_display(None)
        fp =  self.fv.get()
        nf = "CC2_modded_server.exe" if fp == "dedicated_server.exe" else "CC2_modded_game.exe"
        eh = "058fdb1a32950a4be9b22e22d95457b8a5fcc062748e714e8d27e85110458124" if fp == "dedicated_server.exe" else "37847c780814143036c3ddea29954ebc80a8d8a4edacd3a8a5bac00035a64f2a"
        xh = cs256(fp)
        if xh != eh:
            print("Hash check failed")
            input("press enter to quit")
            return

        with open(fp, "rb") as f:
            ba = bytearray(f.read())
        x = self.cv
        for b in x:
            value_to_insert = x[b][1]
            startbyte = offsetDict[b][0]
            reference = il2[b][x[b][0]]
            endbyte = startbyte + len(hexDict[b].replace(" ","")) - 1
            print(startbyte, endbyte)
            searchTerm = struct.pack("<I", reference)
            print(b, searchTerm)
            byte_offset = fo(fp, searchTerm, start=startbyte, end=endbyte)
            print(f"Byte offset: {byte_offset}")
            byte_offset = byte_offset[0]

            if reference >= 150:
                packed_value = struct.pack("<I", value_to_insert)
            else:
                packed_value = struct.pack("<B", value_to_insert)
            ba[byte_offset:byte_offset + len(packed_value)] = packed_value
        print(f"overwriting {len(x)} changes to the file")
        with open(nf, "wb") as f:
            f.write(ba)


def main():
    root = tk.Tk()
    ItemEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

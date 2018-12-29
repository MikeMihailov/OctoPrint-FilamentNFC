material = ['noData',	# 0x00
			'ABS', 		# 0x01 
			'PLA', 		# 0x02
			'Watson', 	# 0x03
			'HiPS',		# 0x04
			'PETG',		# 0x05
			'Nylon',	# 0x06
			'ASA',		# 0x07
			'PVA',		# 0x08
			'PETT',		# 0x09
			'PET',		# 0x0A
			'TPU',		# 0x0B
			'TPE',		# 0x0C
			'PC',		# 0x0D
			'PP',		# 0x0E
			'WOOD'		# 0x0F
]
colorStr = ['noData',	# 0x00
			'white', 	# 0x01,
			'black',	# 0x02,
			'lightGray',# 0x03,
			'gray',		# 0x04,
			'red',		# 0x05,
			'green',	# 0x06,
			'blue',		# 0x07, 
			'yellow',	# 0x08,
			'orange',	# 0x09,
			'brown',	# 0x0A,
			'purple',	# 0x0B,
			'emerald',	# 0x0C,
			'skiey',	# 0x0D,
			'coral',	# 0x0E,
			'rose',		# 0x0F,
			'chocolate',# 0x10,
			'gold',		# 0x11,
			'krem',		# 0x12,
			'limeGreen',# 0x13,
			'lightBlue',# 0x14,
			'natural'	# 0x15
]
colorHex = [0x000000,	# noData
            0xFFFFFF,	# white
            0x000000,	# black
            0xD3D3D3,	# light Gray
            0x808080, 	# gray
            0xFF0000,	# red
            0x00FF00,	# green
            0x0000FF,	# blue
            0xFFFF00,	# erllow
            0xFFA500,	# orange
            0x8B4513,	# brown
            0x800080,	# purple
            0x50C878,	# emerald
            0x87CEEB,	# skiey
            0xF88379,	# coral
            0xB3446C,	# rose
            0x9B5625,	# chocolate
            0xFFDF00,	# gold
            0xFCFBE3,	# krem
            0x32CD32,	# limeGreen
            0xADD8E6,	# lightBlue
            0xEFEFDE	# natural
]


class spool:
    material	= 1					# ABS as default (from matirial list)
    color		= 1  		        # White as default (..)
    weight		= 1000				# gr (1kg as default)
    balance		= weight			# gr (100% as default)
    diametr		= 175				# mm*10^-2
    price		= 1200				# in rus rub as default (The most popular currency in the world ofcause)
    vender		= 'BestFilament'	# text line of 16 char max
    density     = 105               # gr/cm^3 *10^-2
    extMinTemp	= 220				# Extruder minimum temperature, 'C
    extMaxTemp	= 270				# Extruder maximum temperature, 'C
    bedMinTemp	= 90				# Bed minimum temperature, 'C
    bedMaxTemp	= 110				# Bed maximum temperature, 'C
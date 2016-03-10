#https://github.com/thehalftruth/PRIZM-sprite-converter
#Last changes: 10.03.2016
#License: GPLv3 (https://gnu.org/licenses/gpl-3.0.txt)
__version__ = '0.2'


import os
import sys

if sys.version[0] != '2':
    print 'This script require python 2.x'
    raw_input('Press enter to quit')
    exit()
    
try:
    import Image
except ImportError:
    print 'PIL (Python Image Library) is not installed'
    raw_input('Press enter to quit')
    exit()
    
def generate_valid_name(name):
    #if the name is a number add num_ to make the name valid
    try:
        int(name[0])
    except ValueError:
        pass
    else:
        name = 'num_' + name

    name_temp_copy = ''
    
    for char in name:
        if not (char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'):
            name_temp_copy += '_'
        else:
            name_temp_copy += char
            
    return name_temp_copy

def generate_prizm_c_sprite(path, name=None, add_size=True):
    im = Image.open(path)
    new_im = im.convert('RGB')
    pic = new_im.load()
    
    if name is None:
        name = os.path.split(os.path.splitext(path)[0])[1] # use the filename
        
    name = generate_valid_name(name)
            
    sprite_code = 'const color_t %s[] = {' % name
    
    if add_size:
        sprite_code += '\t/*  ' + str(new_im.size[0]) + 'x' + str(new_im.size[1]) + '  */'
    
    sprite_code += '\n\t'
    
    for y in range(new_im.size[1]):
        for x in range(new_im.size[0]):
            r = bin(int((pic[x, y][0] / 8) + 0.5))[2:] #+0.5 to round value
            g = bin(int((pic[x, y][1] / 4) + 0.5))[2:]
            b = bin(int((pic[x, y][2] / 8) + 0.5))[2:]
            r = '0' * (5 - len(r)) + r
            g = '0' * (6 - len(g)) + g
            b = '0' * (5 - len(b)) + b
            
            hex_ = hex(int(r + g + b, 2))[2:]
            sprite_code += '0x' + ('0' * (4 - len(hex_)) + hex_) + ','
            
            if x == (new_im.size[0]-1):
                sprite_code += '\n\t'

    return sprite_code[:-3] + '\n};'  #remove final comma

def generate_prizm_lua_sprite(path, name=None, add_size=True, just_code=False):
    im = Image.open(path)
    new_im = im.convert('RGB')
    pic = new_im.load()
    
    if not just_code:
        if name is None:
            name = os.path.split(os.path.splitext(path)[0])[1] # use the filename
        
        name = generate_valid_name(name)
                
        sprite_code = '%s = "' % name
        
        if add_size:
            sprite_code = '#  ' + str(new_im.size[0]) + 'x' + str(new_im.size[1]) + '\n' + sprite_code
    else:
        sprite_code = ''
    
    for y in range(new_im.size[1]):
        for x in range(new_im.size[0]):
            r = bin(int((pic[x, y][0] / 8) + 0.5))[2:] #+0.5 to round
            g = bin(int((pic[x, y][1] / 4) + 0.5))[2:]
            b = bin(int((pic[x, y][2] / 8) + 0.5))[2:]
            r = '0' * (5 - len(r)) + r
            g = '0' * (6 - len(g)) + g
            b = '0' * (5 - len(b)) + b
            
            hex_ = hex(int(r + g + b, 2))[2:]
            sprite_code += '0' * (4 - len(hex_)) + hex_
            
    if not just_code:
        sprite_code += '"'

    return sprite_code


def show_help():
    print '''
Help
First argument: programming language c or lua
Second argument (optional, default is on): add image size to code,
0 for off 1 for on

Example: converter.py c 0
Converts all images in the folder to a c file without adding the size to code
To convert images in another folder just change the directory in the shell
'''
    raw_input('Press enter to quit')
    exit()

if __name__ == '__main__':
    args = sys.argv
    
    try:
        if args[1] in ['-h', '-help', '--help', '/?']:
            show_help()
        
        language = args[1]
        add_size_ = True
        
        if len(args) == 3:
            add_size_ = bool(int(args[2]))
    except ValueError:
        show_help()
    except IndexError:
        show_help()
    
    if not (language in ['c', 'lua']):
        show_help()

    func = {'c': generate_prizm_c_sprite, 'lua': generate_prizm_lua_sprite}[language]
    
    with open('sprites.' + {'c': 'h', 'lua': 'lua'}[language], 'w') as sprites_file:
        if language == 'c':
            sprites_file.write('#include <color.h>\n')
            
        for file_ in os.listdir(os.getcwd()):
            if os.path.splitext(file_)[1].lower() in ['.jpg', '.jpeg', '.bmp', '.png', '.gif']:
                sprites_file.write(func(file_, add_size = add_size_) + '\n')

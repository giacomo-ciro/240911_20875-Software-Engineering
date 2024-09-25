import sys

def parse(s):
    lines = s.split('\n', maxsplit = 3)
    header = lines[:3]
    rest = lines[3] if len(lines) >= 4 else ''
    
    header_out = [ ','.join(s.split()[::-1]) for s in header ]
    
    rest_out = []
    
    for token in rest.split():
        try:
            number = int(token)
        except ValueError:
            print('Parse    error')
            return
            
        if number == 0:
            break
        
        rest_out.append(f'0x{int(token):x}')
    
    print('\n'.join(header_out))
    print('\n'.join(rest_out))

    
if len(sys.argv) != 2:
    print("Usage: ex2 <file>")
    exit(0)

with open(sys.argv[1], 'r') as file:
    parse(file.read())

exit(0)

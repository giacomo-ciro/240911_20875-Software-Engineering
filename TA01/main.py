# import argparse

# parser = argparse.ArgumentParser(
#                     prog='ProgramName',
#                     description='What the program does',
#                     epilog='Text at the bottom of help')

# parser.add_argument('filename')
# parser.add_argument('-c', '--count')
# parser.add_argument('-v', '--v', action='store_true')

# args = parser.parse_args()
# print(args)       # nameSpace object
# print(vars(args)) # dict

def  truth_table_2(truth_values):
    print('#    a    b        z')
    print(f'     0    0        {1 if truth_values[0] else 0}')
    print(f'     0    1        {1 if truth_values[1] else 0}')
    print(f'     1    0        {1 if truth_values[2] else 0}')
    print(f'     1    1        {1 if truth_values[3] else 0}')

'''
- Bitwise AND (&)
Compare the binary representation of two numbers bit by bit.
It only returns 1 if both bits in the same position are 1;
otherwise, it returns 0.
'''
for i in range(2 ** 4):
    truth_values = [ True if (i & (1 << j)) != 0 else False for j in range(4)]
    print(f'\nTruth table {i}:')
    truth_table_2(truth_values)
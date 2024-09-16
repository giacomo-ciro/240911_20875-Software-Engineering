import sys
print(sys.argv)

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
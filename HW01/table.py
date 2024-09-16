import sys
import os
import re

def evaluate_boolean_expression(expr, variables):

    # Function to evaluate 'and', 'or', 'not' expressions
    def apply_operator(op, a, b=None):
        if op == 'and':
            return a and b
        elif op == 'or':
            return a or b
        elif op == 'not':
            return not a

    def recursive_solve(expression):

        # Base case: if it's a single variable, return its boolean value
        if len(expression) == 1:
            if expression[0] in variables:
                return variables[expression[0]]
            elif expression[0] == 'True':
                return True
            elif expression[0] == 'False':
                return False
        
        # Handling parentheses recursively
        stack = []
        i = 0
        while i < len(expression):
            token = expression[i]
            
            if token == '(':
                # Find the matching closing parenthesis
                open_parens = 1
                for j in range(i + 1, len(expression)):
                    if expression[j] == '(':
                        open_parens += 1
                    elif expression[j] == ')':
                        open_parens -= 1
                    if open_parens == 0:
                        # Solve the sub-expression within the parentheses
                        sub_expr_result = recursive_solve(expression[i + 1:j])
                        stack.append(sub_expr_result)
                        i = j  # Move the index to after the closing ')'
                        break

            elif token in ('and', 'or', 'not'):
                # Just add operators to the stack
                stack.append(token)
            else:
                # Add the variable or boolean constant
                stack.append(variables.get(token, token))

            i += 1

        # Now evaluate the expression in the stack (consider 'not', 'and', 'or')
        while 'not' in stack:
            idx = stack.index('not')
            stack[idx:idx+2] = [apply_operator('not', stack[idx+1])]

        while 'and' in stack:
            idx = stack.index('and')
            stack[idx-1:idx+2] = [apply_operator('and', stack[idx-1], stack[idx+1])]

        while 'or' in stack:
            idx = stack.index('or')
            stack[idx-1:idx+2] = [apply_operator('or', stack[idx-1], stack[idx+1])]

        return stack[0]
    
    # Start the recursive solving process
    return recursive_solve(expr)

class Compiler():
    
    def __init__(self,
                 )->None:    
        
        self.vars = []
        self.ids = {}
        self.table = []

        return
    
    def tokenize(self,
                 s: str=None
                 )->str:
        '''
        
        Tokenize input.txt converted to string according to tokenization rules.
            
            s:
                <str>:
                    the string of raw text to be tokenized

        Returns a list of tokens, i.e., a <list> of <str>

        '''
        # 1.    Anything on a line after the character “#” is ignored.
        s = re.sub(pattern = r"#.+\n",
                   repl = "",
                   string=s
                   )
        tokens = []
        word = []
        for char in s:

            # WORDS -- > starts with a letter or an underscore (no digits)
            if re.match(r'[A-Za-z_]', char) and not word:   
                word.append(char)
            elif re.match(r'[0-9]', char) and not word:
                print('WARNING: encountered word starting with a digit')
            
            # WORDS --> any sequence of (one or more) consecutive letters, digits, or underscores
            elif re.match(r'[A-Za-z_0-9]', char) and word:
                word.append(char)
            
            # BLANKS --> spaces, tabs, carriage, newlines markd the end of a word
            elif re.match(r'[\s]', char) and word:  # [\s] == [\t\n\r' ']
                tokens.append(''.join(word))
                word = []
            
            # SPECIAL chars
            elif re.match(r'[()=;]', char):
                if word:    # special char ends a word
                    tokens.append(''.join(word))
                    word = []
                tokens.append(char)

        return tokens
    
    def parse(self,
              tokens: list=None
        )->None:
        """
        
        Parses the input according to parsing rules. Executes all the instructions and prints show when required.

            tokens:
                <list>:
                    a list of valid tokens.
        Returns

        """
        # Divide instructions
        instructions = []
        buffer = []
        for t in tokens:
            if t == ';':
                instructions.append(buffer)
                buffer = []
            else:
                buffer.append(t)
        
        # Process instructions
        for i in instructions:

            # DECLARATION -> store in self.vars
            if i[0] == 'var':
                for t in i[1:]:
                    if t == ';':
                        break
                    self.vars.append(t)
            
            # ASSIGNMENT -> store in self.ids as ('z', ['x', 'and', 'y'])
            elif i[1] == '=':
                if (i[0] not in self.vars) and (i[0] not in self.ids):
                    buffer = []
                    for t in i[2:]:
                        if t == ';':
                            break
                        buffer.append(t)
                    self.ids[i[0]] = buffer
                else:
                    raise Exception(f"{i[0]} already exists.")
            

            # SHOW
            elif i[0] == 'show' or i[0] == 'show_ones':
                ids_to_show = i[1:]
                self._evaluate()     # exclude 'show'/'show_ones' and ';'
                self._show(ids_to_show, show_ones=i[0] == 'show_ones')

            # INVALID
            else:
                raise Exception(f"{i} is an invalid instruction")
        
        pass

    def _evaluate(self):

        vars = self.vars
        n = len(vars)
        for i in range(2**n):
            variables_truth_values = [ True if (i & (1 << j)) != 0 else False for j in range(n)]
            res = dict(zip(vars, variables_truth_values))
            # evaluate all ids (to avoid issues if back references among ids)
            for id in self.ids.keys():
                res[id] = evaluate_boolean_expression(self.ids[id], res)
            
            self.table.append(res)
    
    def _show(self,
              ids_to_show: list=None,
              show_ones: bool=False
              )->None:
        """
        
        Shows the truth table for a list of identifiers. If show_ones == True, only 
        rows for which at least one identifiers is true are shown
        
        """
        if show_ones:
            valid_row = False
        else:
            valid_row = True
        print('#' + ' ' + ' '.join(self.vars) + '   ' + ' '.join(ids_to_show))
        for row in self.table:
            current_row = ' '
            for var in self.vars:
                current_row += ' 1' if row[var] else ' 0'
            current_row += '  '
            for id in ids_to_show:
                current_row += ' 1' if row[id] else ' 0'
                if row[id]:
                    valid_row = True
            if valid_row:
                print(current_row)
                valid_row = False if show_ones else True

compiler = Compiler()

with open(sys.argv[1], 'r') as f:
    
    f = f.read()
    print(f"Input:\n\n{f}\n\n")
    
    tokens = compiler.tokenize(f)
    print(f'Tokenized Input:\n\n{tokens}\n\n')

    compiler.parse(tokens)
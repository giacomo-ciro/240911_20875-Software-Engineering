import sys
import os
import re

def evaluate_boolean_expression(expr, variables):

    # Function to evaluate 'and', 'or', 'not' expressions
    def apply_operator(op, a, b=None):
        
        # check validity of variables
        if (a not in variables.keys()) and (a not in (True, False)):
            raise Exception(f"Unknown variable '{a}'")
        elif (b != None) and ( b not in variables.keys()) and (b not in (True, False)):
            raise Exception(f"Unkown variable '{b}'")
        
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
            else:
                raise Exception(f"Invalid expression {expression[0]}")
        
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
    
    def _tokenize(self,
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
                raise Exception('Invalid word starting with a digit')
            
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
    
    def _parse(self,
              tokens: list=None,
              verbose: bool=False
        )->None:
        """
        
        Parses the input according to parsing rules.
        Identifies the instructions and executes them.
        Prints the truth tables when required.

        tokens:
            <list>:
                a list of valid tokens.
        verbose:
            <bool>:
                whether to print intermediate steps.

        """
        # Divide instructions
        instructions = []
        buffer = []
        re_evaluate = True  # a flag to re-evaluate the truth table when new variables are declared or assignments are made
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
                re_evaluate = True
                if verbose:
                    print(f'Declaration: {i}')
                for t in i[1:]:
                    if t == ';':
                        break
                    self.vars.append(t)
            
            # ASSIGNMENT -> store in self.ids as ('z', ['x', 'and', 'y'])
            elif i[1] == '=':
                re_evaluate = True
                if verbose:
                    print(f'Assignment: {i}')
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
                if verbose:
                    print(f'Show: {i}')
                ids_to_show = i[1:]
                if re_evaluate:
                    self._evaluate(verbose=verbose)     # evaluate all ids to avoid back-references problems
                    re_evaluate = False
                self._show(ids_to_show, show_ones=i[0] == 'show_ones')

            # INVALID
            else:
                raise Exception(f"{i} is an invalid instruction")
        
        pass

    def _evaluate(self,
                  verbose: bool=False,
                  )->None:
        """
        
        Create the truth table with all identifiers in self.ids and all variables in self.vars.
        The truth table is represented as a list of dictionaries, each representing one row.
        It is stored in self.table.
        
        """
        self.table = []
        vars = self.vars
        n = len(vars)
        
        for i in range(2**n):
            
            if verbose:
                print(f"Evaluating row {i}/{2**n}")
            
            # generate all possible combinations of True/False, viewed as binary numbers monotonically increasing    
            variables_truth_values = [ True if (i & (1 << j)) != 0 else False for j in range(n-1, -1, -1)]
            row = dict(zip(vars, variables_truth_values))

            for id in self.ids.keys():
                if verbose:
                    print(f"    Evaluating {id}")
                row[id] = evaluate_boolean_expression(self.ids[id], row)
            
            self.table.append(row)
        
        return
    
    def _show(self,
              ids_to_show: list=None,
              show_ones: bool=False
              )->None:
        """
        
        Shows the truth table for a list of identifiers.

        ids_to_show:
            <list>:
                a list of identifiers to show in the truth table.
        show_ones:
            <bool>:
                whether to show only rows where at least one identifier takes a value of 1.
        
        """
        valid_row = not show_ones
        print('#' + ' ' + ' '.join(self.vars) + '   ' + ' '.join(ids_to_show))
        for row in self.table:
            current_row = ' '
            for var in self.vars:
                current_row += ' 1' if row[var] else ' 0'
            current_row += '  '
            for id in ids_to_show:
                if id not in row.keys():
                    raise Exception(f"Unknown identifier '{id}'")
                current_row += ' 1' if row[id] else ' 0'
                if row[id]:
                    valid_row = True
            if valid_row:
                print(current_row)
                valid_row = False if show_ones else True
        
        return
        
    def compile(self,
                f,
                verbose=False
                )->None:
        """
        
        Compiles the input string f by first tokenizing it and then parsing it.
        Always prints the requested truth tables to the console. If required, prints also intermediate steps.

        f:
            <str>:
                the input string to be compiled.
        verbose:
            <bool>:
                whether to print intermediate steps.
        
        """
        
        if verbose:
            print(f"Input:\n\n{f}\n\n")
        
        tokens = self._tokenize(f)
        
        if verbose:
            print(f'Tokenized Input:\n\n{tokens}\n\n')
        
        self._parse(tokens, verbose=verbose)


with open(sys.argv[1], 'r') as f:

    compiler = Compiler()    
    f = f.read()
    compiler.compile(f, verbose=True)
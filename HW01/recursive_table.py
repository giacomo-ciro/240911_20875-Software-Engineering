import sys
import re

def check_valid(expr):
    if ('or' in expr) and ('not' in expr):
            raise Exception(f'Conflicts of operators in <{expr}>')
    if ('and' in expr) and ('not' in expr):
            raise Exception(f'Conflicts of operators in <{expr}>')
    if ('and' in expr) and ('or' in expr):
            raise Exception(f'Conflicts of operators in <{expr}>')
    return True

def cast_list(input_list):
    stack = []
    result = []
    temp = []

    for item in input_list:
        if item == '(':
            check_valid(result)
            stack.append(result)
            result = []
        elif item == ')':
            if stack:
                check_valid(result)
                temp = result
                result = stack.pop()
                result.append(temp)
        else:
            result.append(item)
    
    # check validity
    
    check_valid(result)
    return result

def evaluate_expression(expr, row, cache):

    def solve(expr):

        # Base case
        if str(expr) in row:
            return row[str(expr)]
        elif str(expr) == 'False':
            return False
        elif str(expr) == 'True':
            return True
        elif str(expr) in cache:
            return cache[str(expr)]
        
        # Short-circuit evaluation
        for i in range(len(expr)):
            if isinstance(expr[i], list):
                if str(expr[i]) in cache:
                    expr[i] = cache[str(expr[i])]
            elif expr[i] in row:
                expr[i] = row[expr[i]]
        
        if ('and' in expr) and (False in expr):
            # print('shortcut')
            return False
        elif ('or' in expr) and (True in expr):
            # print('shortcut')
            return True
        
        
        # Recursion
        while 'not' in expr:
            ix = expr.index('not')
            key = str(['not', expr[ix+1]])
            cache[key] = not solve(expr[ix+1])
            expr[ix:ix+2] = [cache[key]]

        while 'and' in expr:
            ix = expr.index('and')
            key = str([expr[ix-1], 'and', expr[ix+1]])
            a = solve(expr[ix-1])
            if not a:
                cache[key] = False
                expr[ix-1:ix+2] = [cache[key]]
            cache[key] = a and solve(expr[ix+1])
            expr[ix-1:ix+2] = [cache[key]]
        
        while 'or' in expr:
            ix = expr.index('or')
            key = str([expr[ix-1], 'or', expr[ix+1]])
            a = solve(expr[ix-1])
            if a:
                cache[key] = True
                expr[ix-1:ix+2] = [cache[key]]
            cache[key] = a or solve(expr[ix+1]) 
            expr[ix-1:ix+2] = [cache[key]]   

        return expr[0]  
        
    return solve(expr)


class Compiler():
    
    def __init__(self,
                 )->None:    
        
        self.vars = []      # variables declared so far
        self.ids = {}       # identifiers and their boolean expressions assigned so far

        return

    def _tokenize(self,
                 s: str=None,
                 verbose: bool=False
                 )->str:
        '''
        
        Tokenize input.txt converted to string according to tokenization rules.
            
        s:
            <str>:
                the string of raw text to be tokenized
        verbose:
            <bool>:
                whether to print the final tokens.

        Returns a list of tokens, i.e., a <list> of <str>

        '''
        # 1.    Anything on a line after the character “#” is ignored.
        s = re.sub(pattern = r"#.+\n",
                   repl = "",
                   string=s
                   )
        tokens = []
        word = ''
        for char in s:

            # WORDS -- > starts with a letter or an underscore (no digits)
            if re.match(r'[A-Za-z_]', char) and not word:   
                word += char
            elif re.match(r'[0-9]', char) and not word:
                raise Exception('Invalid word starting with a digit')
            
            # WORDS --> any sequence of (one or more) consecutive letters, digits, or underscores
            elif re.match(r'[A-Za-z_0-9]', char) and word:
                word += char
            
            # BLANKS --> spaces, tabs, carriage, newlines mark the end of a word
            elif re.match(r'[\s]', char) and word:  # [\s] == [\t\n\r' ']
                tokens.append(word)
                word = ''
            
            # SPECIAL chars
            elif re.match(r'[()=;]', char):
                if word:    # special char ends a word
                    tokens.append(word)
                    word = ''
                tokens.append(char)

        if verbose:
            print(f'Tokenized Input:\n\n{tokens}\n\n')
        return tokens
    
    def _split_instructions(self,
                            tokens: list=None,
                            verbose: bool=None
                            )->list:
        """
        
        Returns the tokens grouped by instructions.
        
        tokens:
            <list>:
                a list of valid tokens.
        
        Returns a list of instructions, each being a list of tokens.
        
        """
        
        if verbose:
            print('Splitting instructions...')

        instructions = []
        buffer = []
        for t in tokens:
            if t == ';':
                instructions.append(buffer)
                buffer = []
            else:
                buffer.append(t)
        
        return instructions
    
    def _execute_instructions(self,
                              instructions: list=None,
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
            
            # ASSIGNMENT -> store in self.ids as {'z': ['x', 'and', 'y']}
            elif i[1] == '=':
                # re_evaluate = True  # re-evaluate all ids after an assignment
                if verbose:
                    print(f'Assignment: {i}')
                if (i[0] not in self.vars) and (i[0] not in self.ids):
                    
                    # validity of the instruction
                    for t in i[2:]:
                        if (t in self.vars) or (t in self.ids) or (re.match(r'[()]', t)) or (t in ['and', 'or', 'not', 'True', 'False']):
                            continue
                        else:
                            raise Exception(f"Invalid token in assignment: '{t}'")
                    # if ('and' in i) and ('or' in i):
                    #     raise Exception(f"{i} contains both OR and AND")
                    # if ('not' in i) and (('and' in i) or ('or') in i):
                    #     raise Exception(f"{i} contains both NOT and OR/AND")
                    self.ids[i[0]] = cast_list(i[2:])
                else:
                    raise Exception(f"{i[0]} already exists.")
            

            # SHOW
            elif i[0] == 'show' or i[0] == 'show_ones':
                if verbose:
                    print(f'Show: {i}')
                ids_to_show = i[1:]
                
                # validity of the instruction
                for id in ids_to_show:
                    if id not in self.ids.keys():
                        raise Exception(f"Unknown identifier '{id}'")
                # if re_evaluate:
                #     self._evaluate(verbose=verbose)     # evaluate all ids to avoid back-references problems
                #     re_evaluate = False
                
                self._show(ids_to_show, show_ones= i[0] == 'show_ones')

            # INVALID
            else:
                raise Exception(f"{i} is an invalid instruction")
        
        pass
    
    def _show(self,
              ids_to_show: list=None,
              show_ones: bool=False
              )->None:
        """
        
        Evaluate the truth table for a list of identifiers and prints it.

        ids_to_show:
            <list>:
                a list of identifiers to show in the truth table.
        show_ones:
            <bool>:
                whether to show only rows where at least one identifier takes a value of 1.
        
        """
        
        
        print('#' + ' ' + ' '.join(self.vars) + '   ' + ' '.join(ids_to_show) + '\n')
        
        n = len(self.vars)
        
        for i in range(2**n):
            if i%1e2 == 0: print(f'row{i:,}/{2**n:,}')
            vars = dict(zip(self.vars, [ True if (i & (1 << j)) != 0 else False for j in range(n-1, -1, -1)]))
            row = ' '
            valid_row = not show_ones
            for v in vars:
                row += ' 1' if vars[v] == True else ' 0'
            row += '  '
            cache = {}
            for id in self.ids.keys():
                cache[id] = evaluate_expression(self.ids[id].copy(), vars, cache)
                if id in ids_to_show:
                    row += ' 1' if cache[id] == True else ' 0'
                    
                    if cache[id] and (not valid_row):
                        valid_row = True
            # break
            if valid_row:
                print(row)

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
        
        tokens = self._tokenize(f,
                                verbose=verbose
                                )
        instructions = self._split_instructions(tokens,
                                                verbose=verbose
                                                )
        self._execute_instructions(instructions,
                                   verbose=verbose
                                   )


with open(sys.argv[1], 'r') as f:

    compiler = Compiler()    
    f = f.read()
    compiler.compile(f, verbose=True)


import sys
import re


def cast_list(input_list):
    stack = []
    result = []
    temp = []

    for item in input_list:
        if item == '(':
            stack.append(result)
            result = []
        elif item == ')':
            if stack:
                temp = result
                result = stack.pop()
                result.append(temp)
        else:
            result.append(item)

    return result


class Compiler():
    
    def __init__(self,
                 )->None:    
        
        self.vars = []      # variables declared in the input
        self.ids = {}       # identifiers and their boolean expressions
        self.output = ''    # all the truth tables to be shown

        return

    def evaluate_expression(self, expr, row, cache):
        # print(expr)
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
            
            # ASSIGNMENT -> store in self.ids as {'z': ['x', 'and', 'y']}
            elif i[1] == '=':
                re_evaluate = True
                if verbose:
                    print(f'Assignment: {i}')
                if (i[0] not in self.vars) and (i[0] not in self.ids):
                    self.ids[i[0]] = []
                    for t in i[2:]:
                        if t == ';':
                            break
                        self.ids[i[0]].append(t)
                else:
                    raise Exception(f"{i[0]} already exists.")
            

            # SHOW
            elif i[0] == 'show' or i[0] == 'show_ones':
                if verbose:
                    print(f'Show: {i}')
                ids_to_show = i[1:]
                if re_evaluate:
                    for id in self.ids:
                        self.ids[id] = cast_list(self.ids[id])
                    self._evaluate(verbose=verbose)     # evaluate all ids to avoid back-references problems
                    re_evaluate = False
                # self._show(ids_to_show, show_ones=i[0] == 'show_ones')

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
        vars = self.vars
        n = len(vars)
        
        for i in range(2**n):
            
            if verbose:
                if i%1e6==0: print(f"Evaluating row {i:,}/{2**n:,}")
            
            # generate all possible combinations of True/False, viewed as binary numbers monotonically increasing    
            variables_truth_values = [ True if (i & (1 << j)) != 0 else False for j in range(n-1, -1, -1)]
            row = dict(zip(vars, variables_truth_values))

            for id in self.ids.keys():
                # if verbose:
                #     print(f"    Evaluating {id}")
                cache = {}
                # print(self.ids)
                self.evaluate_expression(self.ids[id], row, cache)
            
            # print(row)
        
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
        output = '#' + ' ' + ' '.join(self.vars) + '   ' + ' '.join(ids_to_show) + '\n'
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
                output += current_row + '\n'
                valid_row = False if show_ones else True
        
        self.output += output
        return output
        
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
    print(compiler.output)

# with open('./output.txt', 'w') as f:
#     f.write(compiler.output)
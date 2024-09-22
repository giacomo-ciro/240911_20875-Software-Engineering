import sys
import re
from itertools import product

# import time
# start_time = time.time()

def check_valid(expr):
    if ('or' in expr) and ('not' in expr):
            raise Exception(f'Conflicts of operators in <{expr}>')
    if ('and' in expr) and ('not' in expr):
            raise Exception(f'Conflicts of operators in <{expr}>')
    if ('and' in expr) and ('or' in expr):
            raise Exception(f'Conflicts of operators in <{expr}>')
    return True

class Node:
    def __init__(self,
                 value=None,
                 children=None):
        self.value = value
        self.children = children if children else []
        self._depth = None
    
    def eval(self, variables):
        
        if self.value == 'and':
            # for child in sorted(self.children, key=lambda x: x.depth()):
            for child in self.children:
                if not child.eval(variables):
                    return False
            return True
        
        elif self.value == 'or':
            # for child in sorted(self.children, key=lambda x: x.depth()):
            for child in self.children:
                if child.eval(variables):
                    return True
            return False
        
        elif self.value == 'not':
            return not self.children[0].eval(variables)
        
        elif self.value == 'True':
            return True
        
        elif self.value == 'False':
            return False
        
        else:
            return variables[self.value]

    def __repr__(self) -> str:
        return f'<Node> \'{self.value}\' with {len(self.children)} children'

    def depth(self):
        if self._depth is None:
            self._depth = 0 if self.children == [] else 1 + min(self.children, key=lambda x: x.depth()).depth() 
        return self._depth

def build_tree_recursively(expr):
    
    def build_tree(expr):
        children = []
        node_type = None
        i = 0
        while i < len(expr):
            token = expr[i]
            
            if token == '(':
                # Find the matching closing parenthesis
                open_parens = 1
                for j in range(i + 1, len(expr)):
                    if expr[j] == '(':
                        open_parens += 1
                    elif expr[j] == ')':
                        open_parens -= 1
                    if open_parens == 0:
                        # Solve the sub-expr within the parentheses
                        node = build_tree(expr[i + 1:j])
                        children.append(node)
                        i = j  # Move the index to after the closing ')'
                        break
            
            elif token in ('not', 'and', 'or'):
                node_type = token if node_type is None else node_type
            else:
                children.append(Node(token))

            i += 1
        children = sorted(children, key=lambda x: x.depth())
        node = Node(node_type, children)
        return node
    
    tree = build_tree(expr)
    return tree

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
                    self.ids[i[0]] = build_tree_recursively(i[2:])
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
        
        vars_value = list(product([False, True], repeat=len(self.vars)))
           
        for i in range(len(vars_value)):
            # if i%1e6 == 0: print(f'row{i:,}/{len(vars_value):,}')
            # vars = dict(zip(self.vars, [ True if (i & (1 << j)) != 0 else False for j in range(n-1, -1, -1)]))
            vars = dict(zip(self.vars, vars_value[i]))
            row = ' '
            valid_row = not show_ones
            for v in vars:
                row += ' 1' if vars[v] == True else ' 0'
            row += '  '
            # cache = {}
            for id in self.ids.keys():
                vars[id] = self.ids[id].eval(vars)
                if id in ids_to_show:
                    row += ' 1' if vars[id] == True else ' 0'
                    
                    if vars[id] and (not valid_row):
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
    compiler.compile(f, verbose=False)

# print("--- %s seconds ---" % (time.time() - start_time))
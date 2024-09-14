import sys
import os
import re

class Compiler():
    
    def __init__(self,
                 )->None:    
        
        self.vars = []
        self.ids = []
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
        
        Parses the input according to parsing rules. Returns Variable Declarations, Assignments and Show Instructions.

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

            # DECLARATION
            if i[0] == 'var':
                print(f'Declaration: {i}')
                for t in i[1:]:
                    if t == ';':
                        break
                    self.vars.append(t)
            
            # ASSIGNMENT
            elif i[1] == '=':
                print(f'Assignment: {i}')
                if (i[0] not in self.vars) and (i[0] not in self.ids):
                    buffer = []
                    for t in i[2:]:
                        if t == ';':
                            break
                        buffer.append(t)
                    self.ids.append((i[0], buffer))         # e.g. ('z', ['x', 'and', 'y'])
                else:
                    raise Exception(f"{i[0]} already exists.")
            

            # SHOW
            elif i[0] == 'show' or i[0] == 'show_ones':
                print(f'Show: {i}')
                # TODO: when a show instruction is called do the following:
                # evaluate ALL ids (not only the ones to be showed, there might be cross references)
                # show the required ones

            # INVALID
            else:
                raise Exception(f"{i} is an invalid instruction")
        
        pass

    def _solve():
        """

        Solves all the ids in self.ids
        
        """

        # TODO: the value of the vars are binary numbers increasing at each row
        # x y z
        # 0 0 0
        # 0 0 1
        # 0 1 0
        # etc. 
        # so you have a clean way to define raws, just a n bit integers (where n = len(self.vars)) 
        # and the identifiers are obtained as a consequence
    
    def _show(ids):
        """
        
        Shows the truth table for a list of identifiers.
        
        """

compiler = Compiler()

with open(sys.argv[1], 'r') as f:
    
    f = f.read()
    
    print("-"*30)
    print(f"Input of type {type(f)}:")
    print("-"*30)
    print(f)
    
    tokens = compiler.tokenize(f)

    print("-"*30)
    print(f'Tokenized Input:')
    print("-"*30)
    print(tokens)

    print("-"*30)
    print(f'Instructions:')
    print("-"*30)

    compiler.parse(tokens)
    print(compiler.vars)
    print(compiler.ids)